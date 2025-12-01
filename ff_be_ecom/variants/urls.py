from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import (
    VariantViewSet
)
router = DefaultRouter()
router.register(r'variants', VariantViewSet, basename='variants')
urlpatterns = [
    path('', include(router.urls)),
]