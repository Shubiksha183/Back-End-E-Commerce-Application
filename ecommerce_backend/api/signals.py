import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Product
from .documents import ProductDocument

# Set up a logger
logger = logging.getLogger(__name__)

@receiver(post_save, sender=Product)
def index_product(sender, instance, created, **kwargs):
    """Index or update product in Elasticsearch."""
    try:
        if created:
            # Create a new document if the product is newly created
            doc = ProductDocument(
                meta={'id': instance.product_id},  # Use product_id as the document ID
                product_id=instance.product_id,
                name=instance.name,
                slug=instance.slug or '',
                description=instance.description or '',
                category_name=instance.category_name,
                brand=instance.brand or '',
                available_stock=instance.available_stock,
                marked_price=float(instance.marked_price),
                discount_price=float(instance.discount_price),
                is_active=instance.is_active,
                created_at=instance.created_at,
                updated_at=instance.updated_at,
            )
            doc.save()
        else:
            # Update the existing document if the product is updated
            doc = ProductDocument.get(id=instance.product_id)
            doc.update(
                name=instance.name,
                slug=instance.slug or '',
                description=instance.description or '',
                category_name=instance.category_name,
                brand=instance.brand or '',
                available_stock=instance.available_stock,
                marked_price=float(instance.marked_price),
                discount_price=float(instance.discount_price),
                is_active=instance.is_active,
                created_at=instance.created_at,
                updated_at=instance.updated_at,
            )
            doc.save()
    except Exception as e:
        logger.error(f"Error indexing product {instance.product_id} in Elasticsearch: {e}")
        print(f"Error indexing product {instance.product_id} in Elasticsearch: {e}")

@receiver(post_delete, sender=Product)
def delete_product(sender, instance, **kwargs):
    """Delete product from Elasticsearch."""
    try:
        # Only delete the document if it exists
        doc = ProductDocument.get(id=instance.product_id)
        doc.delete()
    except Exception as e:
        logger.error(f"Error deleting product {instance.product_id} from Elasticsearch: {e}")
        print(f"Error deleting product {instance.product_id} from Elasticsearch: {e}")
