"""
Serializers for the ecommerce app.

This module provides DRF serializers for all ecommerce models,
including nested serializers for related objects.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import (
    Customer, Category, Product, Variant, PricingRule, Promotion,
    InventoryMovement, Cart, CartItem, Order, OrderItem, Review,
    AnalyticsSnapshot
)

User = get_user_model()


class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for Customer model."""
    
    class Meta:
        model = Customer
        fields = ['id', 'user', 'email', 'name', 'phone', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model."""
    
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'slug', 'name', 'description', 'parent', 'children', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_children(self, obj):
        """Return child categories."""
        children = obj.children.all()
        return CategorySerializer(children, many=True).data if children else []


class VariantSerializer(serializers.ModelSerializer):
    """Serializer for Variant model."""
    
    effective_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    
    class Meta:
        model = Variant
        fields = [
            'id', 'product', 'sku', 'name', 'price', 'sale_price',
            'currency', 'stock', 'attributes', 'effective_price'
        ]
        read_only_fields = ['id']


class VariantListSerializer(serializers.ModelSerializer):
    """Simplified serializer for Variant when nested in Product."""
    
    effective_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    
    class Meta:
        model = Variant
        fields = [
            'id', 'sku', 'name', 'price', 'sale_price',
            'currency', 'stock', 'attributes', 'effective_price'
        ]
        read_only_fields = ['id']


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model with nested variants."""
    
    variants = VariantListSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'slug', 'name', 'summary', 'description', 'category',
            'category_name', 'images', 'attributes', 'status',
            'variants', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductListSerializer(serializers.ModelSerializer):
    """Simplified serializer for Product list views."""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    variant_count = serializers.IntegerField(source='variants.count', read_only=True)
    min_price = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'slug', 'name', 'summary', 'category', 'category_name',
            'images', 'status', 'variant_count', 'min_price', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_min_price(self, obj):
        """Return the minimum price from all variants."""
        variants = obj.variants.all()
        if not variants:
            return None
        return min(v.effective_price for v in variants)


class PricingRuleSerializer(serializers.ModelSerializer):
    """Serializer for PricingRule model."""
    
    class Meta:
        model = PricingRule
        fields = [
            'id', 'name', 'type', 'value', 'applies_to',
            'active', 'starts_at', 'ends_at'
        ]
        read_only_fields = ['id']


class PromotionSerializer(serializers.ModelSerializer):
    """Serializer for Promotion model."""
    
    rule_details = PricingRuleSerializer(source='rule', read_only=True)
    is_available = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Promotion
        fields = [
            'id', 'code', 'name', 'description', 'rule',
            'rule_details', 'active', 'usage_limit', 'used_count', 'is_available'
        ]
        read_only_fields = ['id', 'used_count']


class PromotionApplySerializer(serializers.Serializer):
    """Serializer for applying a promotion code."""
    
    code = serializers.CharField(max_length=40)


class InventoryMovementSerializer(serializers.ModelSerializer):
    """Serializer for InventoryMovement model."""
    
    variant_sku = serializers.CharField(source='variant.sku', read_only=True)
    
    class Meta:
        model = InventoryMovement
        fields = ['id', 'variant', 'variant_sku', 'change', 'reason', 'metadata', 'created_at']
        read_only_fields = ['id', 'created_at']


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for CartItem model."""
    
    variant_details = VariantListSerializer(source='variant', read_only=True)
    line_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'variant', 'variant_details', 'qty', 'price_at_add', 'line_total']
        read_only_fields = ['id', 'cart', 'price_at_add', 'line_total']


class CartItemCreateSerializer(serializers.Serializer):
    """Serializer for adding items to cart."""
    
    variant_id = serializers.UUIDField()
    qty = serializers.IntegerField(min_value=1, default=1)


class CartItemUpdateSerializer(serializers.Serializer):
    """Serializer for updating cart item quantity."""
    
    qty = serializers.IntegerField(min_value=1)


class CartSerializer(serializers.ModelSerializer):
    """Serializer for Cart model with nested items."""
    
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'customer', 'status', 'items', 'total', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for OrderItem model."""
    
    variant_details = VariantListSerializer(source='variant', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'variant', 'variant_details', 'qty', 'unit_price', 'line_total']
        read_only_fields = ['id']


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for Order model with nested items."""
    
    items = OrderItemSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'customer', 'customer_name', 'status',
            'subtotal', 'discount_total', 'shipping_total', 'tax_total',
            'grand_total', 'currency', 'payment_ref', 'shipping_address',
            'billing_address', 'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'order_number', 'created_at', 'updated_at']


class OrderCreateSerializer(serializers.Serializer):
    """Serializer for creating an order from checkout."""
    
    shipping_address = serializers.JSONField()
    billing_address = serializers.JSONField(required=False)
    payment_ref = serializers.CharField(max_length=80, required=False, allow_blank=True)


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for Review model."""
    
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'product', 'customer', 'customer_name', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'customer', 'created_at']


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a review."""
    
    class Meta:
        model = Review
        fields = ['rating', 'comment']


class AnalyticsSnapshotSerializer(serializers.ModelSerializer):
    """Serializer for AnalyticsSnapshot model."""
    
    class Meta:
        model = AnalyticsSnapshot
        fields = ['id', 'metric', 'value', 'breakdown', 'period', 'created_at']
        read_only_fields = ['id', 'created_at']
