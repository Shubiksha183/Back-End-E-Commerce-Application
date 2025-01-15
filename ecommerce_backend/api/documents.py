from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl.registries import registry
from .models import Product  # Keep this import for model reference

@registry.register_document
class ProductDocument(Document):
    class Index:
        name = 'products_project_1'

    class Django:
        model = Product
        fields = [
            'name',
            'category_name',  # Updated to match the field in `Product`
            'brand',
            'description',
            'marked_price'
        ]
