from rest_framework import routers
from django.urls import path, include

from .views import (
    CartViewSet
)

router = routers.DefaultRouter()
router.register(r'carts', CartViewSet, basename='carts')
urlpatterns = [
    path('', include(router.urls)),
]