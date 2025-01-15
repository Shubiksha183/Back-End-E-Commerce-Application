from django.core.management.base import BaseCommand
from ...models import Product
from ...documents import ProductDocument

class Command(BaseCommand):
    help = 'Index data into Elasticsearch'

    def handle(self, *args, **kwargs):
        products = Product.objects.all()
        for product in products:
            ProductDocument().update(product)
        self.stdout.write(self.style.SUCCESS('Data indexed successfully!'))
