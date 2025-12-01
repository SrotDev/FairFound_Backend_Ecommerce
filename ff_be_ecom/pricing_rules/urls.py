from rest_framework import routers
from django.urls import path, include

from .views import (
    PricingRuleViewSet
)
router = routers.DefaultRouter()
router.register(r'pricing-rules', PricingRuleViewSet, basename='pricing-rule')
urlpatterns = [
    path('', include(router.urls)),
]