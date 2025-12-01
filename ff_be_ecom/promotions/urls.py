from rest_framework import routers
from django.urls import path, include

from .views import (
    PromotionViewSet
)
router = routers.DefaultRouter()
router.register(r'promotions', PromotionViewSet, basename='promotion')
urlpatterns = [
    path('', include(router.urls)), 
]