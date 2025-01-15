from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import ProductViewSet

# Initialize the router
router = DefaultRouter()
router.register(r'products', ProductViewSet)  # Registers `/api/products/`

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin panel
    path('api/', include(router.urls)),  # API routes for products
    path('api/', include('api.urls')),  # Include app-specific routes under `/api/`
]
