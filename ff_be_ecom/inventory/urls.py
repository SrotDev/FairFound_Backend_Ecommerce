from rest_framework import routers
from django.urls import path, include

from .views import InventoryMovementViewSet

router = routers.DefaultRouter()
router.register(r'inventory-movements', InventoryMovementViewSet, basename='inventory-movements')
urlpatterns = [
    path('', include(router.urls)),
]
