"""
Ecommerce models for the FairFound backend.

This module contains all the data models required for a complete ecommerce system,
including customers, products, categories, variants, pricing, promotions,
inventory, carts, orders, reviews, and analytics.
"""

import uuid
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Customer(models.Model):
    """Customer model representing both registered users and guest customers."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='customer'
    )
    email = models.EmailField()
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=30, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.email})"


class Category(models.Model):
    """Category model for organizing products in a hierarchical structure."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(unique=True, max_length=120)
    name = models.CharField(max_length=120)
    description = models.TextField(null=True, blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Product(models.Model):
    """Product model representing items available for sale."""
    
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        DRAFT = 'draft', 'Draft'
        ARCHIVED = 'archived', 'Archived'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(unique=True, max_length=160)
    name = models.CharField(max_length=160)
    summary = models.TextField()
    description = models.TextField()
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products'
    )
    images = models.JSONField(default=list)  # list of image URLs
    attributes = models.JSONField(default=dict)  # e.g., {color: ["red","blue"], size: ["S","M","L"]}
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Variant(models.Model):
    """Variant model representing specific SKUs of a product."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='variants'
    )
    sku = models.CharField(max_length=80, unique=True)
    name = models.CharField(max_length=160, null=True, blank=True)  # e.g., "Blue / M"
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    currency = models.CharField(max_length=3, default='USD')
    stock = models.IntegerField(default=0)  # on-hand inventory
    attributes = models.JSONField(default=dict)  # e.g., {color: "blue", size: "M"}

    class Meta:
        ordering = ['sku']

    def __str__(self):
        return f"{self.product.name} - {self.sku}"

    @property
    def effective_price(self):
        """Return sale_price if available, otherwise regular price."""
        return self.sale_price if self.sale_price else self.price


class PricingRule(models.Model):
    """Pricing rule model for defining discounts and promotions."""
    
    class RuleType(models.TextChoices):
        PERCENTAGE = 'percentage', 'Percentage'
        FIXED = 'fixed', 'Fixed Amount'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=160)
    type = models.CharField(max_length=20, choices=RuleType.choices)
    value = models.DecimalField(max_digits=10, decimal_places=2)  # percentage or fixed amount
    applies_to = models.JSONField(default=dict)  # product/variant IDs or category filter
    active = models.BooleanField(default=True)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-active', 'name']

    def __str__(self):
        return self.name


class Promotion(models.Model):
    """Promotion model for coupon codes that link to pricing rules."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=160)
    description = models.TextField(null=True, blank=True)
    rule = models.ForeignKey(
        PricingRule,
        on_delete=models.PROTECT,
        related_name='promotions'
    )
    active = models.BooleanField(default=True)
    usage_limit = models.IntegerField(null=True, blank=True)
    used_count = models.IntegerField(default=0)

    class Meta:
        ordering = ['-active', 'name']

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def is_available(self):
        """Check if promotion is still available for use."""
        if not self.active:
            return False
        if self.usage_limit and self.used_count >= self.usage_limit:
            return False
        return True


class InventoryMovement(models.Model):
    """Inventory movement model for tracking stock changes."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    variant = models.ForeignKey(
        Variant,
        on_delete=models.CASCADE,
        related_name='inventory_movements'
    )
    change = models.IntegerField()  # +inbound, -outbound
    reason = models.CharField(max_length=80)  # sale|refund|adjustment|supplier
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.variant.sku}: {self.change:+d} ({self.reason})"


class Cart(models.Model):
    """Cart model for storing customer shopping carts."""
    
    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        CONVERTED = 'converted', 'Converted'
        ABANDONED = 'abandoned', 'Abandoned'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='carts'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        customer_name = self.customer.name if self.customer else 'Guest'
        return f"Cart {self.id} - {customer_name}"

    @property
    def total(self):
        """Calculate the total price of all items in the cart."""
        return sum(item.line_total for item in self.items.all())


class CartItem(models.Model):
    """Cart item model representing products in a shopping cart."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )
    variant = models.ForeignKey(
        Variant,
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    qty = models.IntegerField(default=1)
    price_at_add = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.variant.sku} x {self.qty}"

    @property
    def line_total(self):
        """Calculate the total price for this line item."""
        return self.price_at_add * self.qty


class Order(models.Model):
    """Order model for completed purchases."""
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PAID = 'paid', 'Paid'
        FULFILLED = 'fulfilled', 'Fulfilled'
        CANCELLED = 'cancelled', 'Cancelled'
        REFUNDED = 'refunded', 'Refunded'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=20, unique=True)
    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    payment_ref = models.CharField(max_length=80, null=True, blank=True)
    shipping_address = models.JSONField(default=dict)
    billing_address = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.order_number}"


class OrderItem(models.Model):
    """Order item model representing products in a completed order."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    variant = models.ForeignKey(
        Variant,
        on_delete=models.PROTECT,
        related_name='order_items'
    )
    qty = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    line_total = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.variant.sku} x {self.qty}"


class Review(models.Model):
    """Review model for product ratings and comments."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviews'
    )
    rating = models.SmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Review for {self.product.name} - {self.rating}★"


class AnalyticsSnapshot(models.Model):
    """Analytics snapshot model for storing aggregated metrics."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    metric = models.CharField(max_length=40)  # visibility|conversion_rate|engagement|revenue
    value = models.DecimalField(max_digits=12, decimal_places=2)
    breakdown = models.JSONField(default=dict)
    period = models.CharField(max_length=20)  # e.g., 2025-11 or week-48
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.metric}: {self.value} ({self.period})"
