from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password, check_password
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from .models import CustomUser, Category, Product
from .serializers import CategorySerializer, ProductSerializer
from .documents import ProductDocument
from elasticsearch_dsl import Q
from rest_framework.exceptions import APIException
import re

class ProductPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class SignupView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        data = request.data
        email = data.get('email')
        name = data.get('name')
        password = data.get('password')

        if not email or not name or not password:
            return Response({"message": "All fields are required (name, email, password)."}, status=status.HTTP_400_BAD_REQUEST)

        if CustomUser.objects.filter(email=email).exists():
            return Response({"message": "User with this email already exists"}, status=status.HTTP_400_BAD_REQUEST)

        hashed_password = make_password(password)
        try:
            CustomUser.objects.create(name=name, email=email, password=hashed_password)
            return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"message": f"Error creating user: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SigninView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        data = request.data
        name = data.get('name')
        password = data.get('password')

        try:
            user = CustomUser.objects.get(name=name)
            if check_password(password, user.password):
                refresh = RefreshToken.for_user(user)
                return Response({
                    "message": "Signin successful.",
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                }, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
        except CustomUser.DoesNotExist:
            return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)

class CategoryListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

from rest_framework import viewsets

from rest_framework.filters import SearchFilter
from django.db.models import Q

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('name')  # Order the queryset
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ProductPagination  # Custom paginator

    def get_queryset(self):
        queryset = self.queryset  # Use the ordered queryset
        request = self.request
        category_ids = request.query_params.get('category_id', None)
        search_query = request.query_params.get('query', None)

        # Filter by category_id if provided
        if category_ids:
            category_ids = category_ids.split(',')
            queryset = queryset.filter(category_id__in=category_ids)

        # Apply search filter if search_query is provided
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(category_name__icontains=search_query)|
                Q(brand__icontains=search_query)
            )

        return queryset

class ProtectedView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        print(f"Authenticated user: {request.user}")

        return Response({"message": "This is a protected view."})
    

    from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from elasticsearch_dsl import Q
from rest_framework.pagination import PageNumberPagination
from .documents import ProductDocument


class SearchPagination(PageNumberPagination):
    page_size = 10  # Number of items per page


class ProductSearchView(APIView):
    """
    API View for searching products using Elasticsearch with advanced query parsing.
    """
    pagination_class = SearchPagination

    def parse_query(self, query):
        """
        Parses a user query to extract structured components like price filters and brand.
        """
        import re

        parsed = {"query": query}
        # Extract price conditions
        match = re.search(r"under\s+(\d+)", query, re.IGNORECASE)
        if match:
            parsed["max_price"] = float(match.group(1))

        match = re.search(r"above\s+(\d+)", query, re.IGNORECASE)
        if match:
            parsed["min_price"] = float(match.group(1))

        # Extract brand using "in {brand}" pattern
        match = re.search(r"in\s+(\w+)", query, re.IGNORECASE)
        if match:
            parsed["brand"] = match.group(1).lower()

        # Remove keywords (under, above, in) from the query
        parsed["query"] = re.sub(r"(under|above|in)\s+\w+", "", query, flags=re.IGNORECASE).strip()

        return parsed

    def get(self, request):
        # Get the search query from the request parameters
        user_query = request.query_params.get('q', '')
        if not user_query:
            return Response(
                {"error": "Query parameter `q` is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Parse the query into structured components
        parsed_query = self.parse_query(user_query)
        print(f"Parsed Query: {parsed_query}")  # Debugging parsed query

        # Full-text search
        search_query = Q(
            "multi_match",
            query=parsed_query.get("query", ""),
            fields=["name", "description", "category_name", "brand"],
            operator="and",
        )

        # Filters
        filters = Q()
        if parsed_query.get("brand"):
            filters &= Q("term", brand=parsed_query["brand"])
        if parsed_query.get("max_price"):
            filters &= Q("range", marked_price={"lte": parsed_query["max_price"]})
        if parsed_query.get("min_price"):
            filters &= Q("range", marked_price={"gte": parsed_query["min_price"]})

        final_query = search_query & filters

        # Debugging queries
        print(f"Search Query: {search_query}")
        print(f"Filters: {filters}")
        print(f"Final Query: {final_query}")

        # Execute the search
        search = ProductDocument.search().query(final_query)
        results = search.execute()

        # Paginate results
        paginator = self.pagination_class()
        results_list = list(results)
        paginated_results = paginator.paginate_queryset(results_list, request)

        if not results_list:
            # Provide recommendations when no results are found
            recommendations = ProductDocument.search().sort("-marked_price")[:5].execute()
            return Response({
                "results": [],
                "recommendations": [hit.to_dict() for hit in recommendations],
            })

        return paginator.get_paginated_response([hit.to_dict() for hit in paginated_results])

