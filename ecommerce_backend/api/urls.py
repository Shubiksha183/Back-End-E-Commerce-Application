from django.urls import path
from .views import SignupView, SigninView, CategoryListView, ProductSearchView

app_name = "api"

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),  # User signup
    path('signin/', SigninView.as_view(), name='signin'),  # User signin
    path('categories/', CategoryListView.as_view(), name='categories'),  # Fetch categories
    path('search/', ProductSearchView.as_view(), name='product-search'),  # Product search
]
