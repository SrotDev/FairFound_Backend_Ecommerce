"""
Admin configuration for the ecommerce app.

This module registers all ecommerce models with the Django admin interface.
"""

from django.contrib import admin
from .models import (
    Customer, Category, Product, Variant, PricingRule, Promotion,
    InventoryMovement, Cart, CartItem, Order, OrderItem, Review,
    AnalyticsSnapshot
)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """Admin configuration for Customer model."""
    
    list_display = ['name', 'email', 'phone', 'created_at']
    search_fields = ['name', 'email', 'phone']
    list_filter = ['created_at']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin configuration for Category model."""
    
    list_display = ['name', 'slug', 'parent', 'created_at']
    search_fields = ['name', 'slug']
    list_filter = ['parent', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['id', 'created_at']


class VariantInline(admin.TabularInline):
    """Inline admin for Variant model."""
    
    model = Variant
    extra = 1
    fields = ['sku', 'name', 'price', 'sale_price', 'currency', 'stock', 'attributes']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin configuration for Product model."""
    
    list_display = ['name', 'slug', 'category', 'status', 'created_at']
    search_fields = ['name', 'slug', 'summary']
    list_filter = ['status', 'category', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [VariantInline]


@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
    """Admin configuration for Variant model."""
    
    list_display = ['sku', 'product', 'price', 'sale_price', 'stock', 'currency']
    search_fields = ['sku', 'name', 'product__name']
    list_filter = ['product', 'currency']
    readonly_fields = ['id']


@admin.register(PricingRule)
class PricingRuleAdmin(admin.ModelAdmin):
    """Admin configuration for PricingRule model."""
    
    list_display = ['name', 'type', 'value', 'active', 'starts_at', 'ends_at']
    search_fields = ['name']
    list_filter = ['type', 'active', 'starts_at', 'ends_at']
    readonly_fields = ['id']


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    """Admin configuration for Promotion model."""
    
    list_display = ['code', 'name', 'rule', 'active', 'usage_limit', 'used_count']
    search_fields = ['code', 'name']
    list_filter = ['active', 'rule']
    readonly_fields = ['id', 'used_count']


@admin.register(InventoryMovement)
class InventoryMovementAdmin(admin.ModelAdmin):
    """Admin configuration for InventoryMovement model."""
    
    list_display = ['variant', 'change', 'reason', 'created_at']
    search_fields = ['variant__sku', 'reason']
    list_filter = ['reason', 'created_at']
    readonly_fields = ['id', 'created_at']


class CartItemInline(admin.TabularInline):
    """Inline admin for CartItem model."""
    
    model = CartItem
    extra = 0
    fields = ['variant', 'qty', 'price_at_add']
    readonly_fields = ['price_at_add']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Admin configuration for Cart model."""
    
    list_display = ['id', 'customer', 'status', 'created_at', 'updated_at']
    search_fields = ['customer__name', 'customer__email']
    list_filter = ['status', 'created_at']
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [CartItemInline]


class OrderItemInline(admin.TabularInline):
    """Inline admin for OrderItem model."""
    
    model = OrderItem
    extra = 0
    fields = ['variant', 'qty', 'unit_price', 'line_total']
    readonly_fields = ['line_total']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin configuration for Order model."""
    
    list_display = ['order_number', 'customer', 'status', 'grand_total', 'currency', 'created_at']
    search_fields = ['order_number', 'customer__name', 'customer__email']
    list_filter = ['status', 'currency', 'created_at']
    readonly_fields = ['id', 'order_number', 'created_at', 'updated_at']
    inlines = [OrderItemInline]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin configuration for Review model."""
    
    list_display = ['product', 'customer', 'rating', 'created_at']
    search_fields = ['product__name', 'customer__name', 'comment']
    list_filter = ['rating', 'created_at']
    readonly_fields = ['id', 'created_at']


@admin.register(AnalyticsSnapshot)
class AnalyticsSnapshotAdmin(admin.ModelAdmin):
    """Admin configuration for AnalyticsSnapshot model."""
    
    list_display = ['metric', 'value', 'period', 'created_at']
    search_fields = ['metric', 'period']
    list_filter = ['metric', 'period', 'created_at']
    readonly_fields = ['id', 'created_at']
