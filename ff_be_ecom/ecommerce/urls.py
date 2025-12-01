"""
URL configuration for the ecommerce app.

This module defines the API routes for all ecommerce endpoints
using DRF routers for ViewSets.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CustomerViewSet, CategoryViewSet, ProductViewSet, VariantViewSet,
    PricingRuleViewSet, PromotionViewSet, InventoryMovementViewSet,
    CartViewSet, OrderViewSet, ReviewViewSet, AnalyticsSnapshotViewSet
)

app_name = 'ecommerce'

router = DefaultRouter()
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'variants', VariantViewSet, basename='variant')
router.register(r'pricing-rules', PricingRuleViewSet, basename='pricing-rule')
router.register(r'promotions', PromotionViewSet, basename='promotion')
router.register(r'carts', CartViewSet, basename='cart')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'reviews', ReviewViewSet, basename='review')

# Nested router for inventory movements
inventory_router = DefaultRouter()
inventory_router.register(r'movements', InventoryMovementViewSet, basename='inventory-movement')

# Nested router for analytics
analytics_router = DefaultRouter()
analytics_router.register(r'snapshots', AnalyticsSnapshotViewSet, basename='analytics-snapshot')

urlpatterns = [
    path('', include(router.urls)),
    path('inventory/', include(inventory_router.urls)),
    path('analytics/', include(analytics_router.urls)),
]
