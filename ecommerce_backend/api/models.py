from django.db import models
from django.utils.text import slugify
from PIL import Image
from io import BytesIO
from django.core.files import File
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission

from elasticsearch_dsl import connections

# Connect to Elasticsearch
connections.create_connection(hosts=['http://localhost:9200'])

# Lazy import to avoid circular dependency
def get_product_document():
    from .documents import ProductDocument
    return ProductDocument


# Custom user manager
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


# Custom user model
class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    groups = models.ManyToManyField(
        Group,
        related_name="customuser_groups",
        blank=True,
        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="customuser_permissions",
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.name


# Category model
class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=255, unique=True)
    date_of_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.category_name


# Product model
class Product(models.Model):
    CATEGORY_CHOICES = [
        ('electronics', 'Electronics'),
        ('fashion', 'Fashion'),
        ('home_appliances', 'Home Appliances'),
        ('books', 'Books'),
        ('others', 'Others'),
    ]

    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    category_id = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='products')
    category_name = models.CharField(max_length=255, choices=CATEGORY_CHOICES, default='fashion')
    brand = models.CharField(max_length=255, null=True, blank=True)
    available_stock = models.IntegerField()
    marked_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        if self.image:
            self.image = self.compress_image(self.image)

        # Index document in Elasticsearch
        product_doc = get_product_document()(
            meta={'id': self.product_id},
            name=self.name,
            category=self.category_name,
            brand=self.brand,
            description=self.description,
        )
        product_doc.save()

        super(Product, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        try:
            product_doc = get_product_document().get(id=self.product_id)
            product_doc.delete()
        except Exception as e:
            print(f"Error deleting document from Elasticsearch: {e}")

        super(Product, self).delete(*args, **kwargs)

    @staticmethod
    def compress_image(image):
        img = Image.open(image)
        img = img.convert("RGB")
        img_io = BytesIO()
        img.save(img_io, "JPEG", quality=85)
        img_io.seek(0)
        return File(img_io, name=image.name)

    def __str__(self):
        return self.name
