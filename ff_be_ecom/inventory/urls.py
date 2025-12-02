from rest_framework import routers
from django.urls import path, include

from .views import InventoryMovementViewSet

router = routers.DefaultRouter()
# Register under `movements` so the full URL becomes:
# /api/ecommerce/inventory/movements/
router.register(r'inventory', InventoryMovementViewSet, basename='inventory-movements')
urlpatterns = [
    path('', include(router.urls),
         ),
]
