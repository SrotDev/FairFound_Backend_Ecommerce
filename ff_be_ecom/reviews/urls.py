from rest_framework import routers
from django.urls import path, include

from .views import (
    ReviewViewSet
)

router = routers.DefaultRouter()
router.register(r'reviews', ReviewViewSet, basename='review')
urlpatterns = [
    path('', include(router.urls)),
]