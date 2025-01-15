from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from elasticsearch_dsl.query import MultiMatch
from .documents import ProductDocument

class ProductSearchView(APIView):
    """
    API View for searching products using Elasticsearch.
    """

    def get(self, request):
        # Get the search query from the request parameters
        query = request.query_params.get('q', '')
        if not query:
            return Response(
                {"error": "Query parameter `q` is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Elasticsearch query: MultiMatch search across multiple fields
        search = ProductDocument.search().query(
            MultiMatch(
                query=query,
                fields=['name', 'category_name', 'brand', 'description'],  # Updated field names
                fuzziness='auto'  # Allow fuzzy matching for better results
            )
        )

        # Execute the search and fetch results
        results = search.execute()

        # Prepare the response data
        response_data = [
            {
                'id': hit.meta.id,
                'name': hit.name,
                'category_name': hit.category_name,
                'brand': hit.brand,
                'description': hit.description,
            }
            for hit in results
        ]

        return Response(response_data, status=status.HTTP_200_OK)