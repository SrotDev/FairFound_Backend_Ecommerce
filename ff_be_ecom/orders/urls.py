from rest_framework import routers
from django.urls import path, include

from .views import (
    OrderViewSet
)

router = routers.DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')
urlpatterns = [
    path('', include(router.urls)),
]