"""
Views and ViewSets for the ecommerce app.

This module provides DRF ViewSets for all ecommerce models,
including custom actions for carts, orders, and promotions.
"""

import uuid
from decimal import Decimal
from django.shortcuts import get_object_or_404
from django.db import transaction
from django_filters import rest_framework as filters
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import (
    Customer, Category, Product, Variant, PricingRule, Promotion,
    InventoryMovement, Cart, CartItem, Order, OrderItem, Review,
    AnalyticsSnapshot
)
from .serializers import (
    CustomerSerializer, CategorySerializer, ProductSerializer,
    ProductListSerializer, VariantSerializer, PricingRuleSerializer,
    PromotionSerializer, PromotionApplySerializer, InventoryMovementSerializer,
    CartSerializer, CartItemSerializer, CartItemCreateSerializer,
    CartItemUpdateSerializer, OrderSerializer, OrderCreateSerializer,
    ReviewSerializer, ReviewCreateSerializer, AnalyticsSnapshotSerializer
)


class IsAdminOrReadOnly(permissions.BasePermission):
    """Allow read access to all, but write access only to admins."""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class IsOwnerOrAdmin(permissions.BasePermission):
    """Allow access to object owner or admin users."""
    
    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True
        if hasattr(obj, 'customer') and obj.customer:
            return obj.customer.user == request.user
        return False


class ProductFilter(filters.FilterSet):
    """Filter for Product list view."""
    
    category = filters.UUIDFilter(field_name='category__id')
    category_slug = filters.CharFilter(field_name='category__slug')
    status = filters.CharFilter(field_name='status')
    search = filters.CharFilter(method='filter_search')
    min_price = filters.NumberFilter(method='filter_min_price')
    max_price = filters.NumberFilter(method='filter_max_price')
    
    class Meta:
        model = Product
        fields = ['category', 'category_slug', 'status']
    
    def filter_search(self, queryset, name, value):
        """Search in name, summary, and description."""
        return queryset.filter(name__icontains=value)
    
    def filter_min_price(self, queryset, name, value):
        """Filter by minimum price (checks variants)."""
        return queryset.filter(variants__price__gte=value).distinct()
    
    def filter_max_price(self, queryset, name, value):
        """Filter by maximum price (checks variants)."""
        return queryset.filter(variants__price__lte=value).distinct()


class CustomerViewSet(viewsets.ModelViewSet):
    """ViewSet for Customer model."""
    
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAdminUser]
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """Get the current user's customer profile."""
        customer = get_object_or_404(Customer, user=request.user)
        serializer = self.get_serializer(customer)
        return Response(serializer.data)


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for Category model."""
    
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'pk'
    filterset_fields = ['parent']
    search_fields = ['name', 'slug']
    ordering_fields = ['name', 'created_at']


class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet for Product model."""
    
    queryset = Product.objects.prefetch_related('variants').select_related('category')
    permission_classes = [IsAdminOrReadOnly]
    filterset_class = ProductFilter
    search_fields = ['name', 'summary', 'description']
    ordering_fields = ['name', 'created_at', 'updated_at']
    lookup_field = 'pk'
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductSerializer
    
    def get_queryset(self):
        """Optionally filter by slug for retrieve."""
        queryset = super().get_queryset()
        # Allow public access to active products only for non-admin users
        if not (self.request.user and self.request.user.is_staff):
            queryset = queryset.filter(status=Product.Status.ACTIVE)
        return queryset
    
    @action(detail=True, methods=['get'])
    def variants(self, request, pk=None):
        """List variants for a specific product."""
        product = self.get_object()
        variants = product.variants.all()
        serializer = VariantSerializer(variants, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get', 'post'])
    def reviews(self, request, pk=None):
        """List or create reviews for a specific product."""
        product = self.get_object()
        
        if request.method == 'GET':
            reviews = product.reviews.all()
            serializer = ReviewSerializer(reviews, many=True)
            return Response(serializer.data)
        
        # POST - create review
        serializer = ReviewCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get or create customer for the user
        customer, _ = Customer.objects.get_or_create(
            user=request.user,
            defaults={'email': request.user.email, 'name': request.user.get_full_name() or request.user.username}
        )
        
        review = Review.objects.create(
            product=product,
            customer=customer,
            rating=serializer.validated_data['rating'],
            comment=serializer.validated_data['comment']
        )
        
        return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)


class VariantViewSet(viewsets.ModelViewSet):
    """ViewSet for Variant model."""
    
    queryset = Variant.objects.select_related('product')
    serializer_class = VariantSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ['product']
    search_fields = ['sku', 'name']
    ordering_fields = ['sku', 'price']


class PricingRuleViewSet(viewsets.ModelViewSet):
    """ViewSet for PricingRule model."""
    
    queryset = PricingRule.objects.all()
    serializer_class = PricingRuleSerializer
    permission_classes = [permissions.IsAdminUser]
    filterset_fields = ['active', 'type']
    ordering_fields = ['name', 'starts_at', 'ends_at']


class PromotionViewSet(viewsets.ModelViewSet):
    """ViewSet for Promotion model."""
    
    queryset = Promotion.objects.select_related('rule')
    serializer_class = PromotionSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ['active']
    search_fields = ['code', 'name']
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def apply(self, request):
        """Preview applying a promotion code to see the discount."""
        serializer = PromotionApplySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        code = serializer.validated_data['code']
        promotion = get_object_or_404(Promotion, code__iexact=code)
        
        if not promotion.is_available:
            return Response(
                {'detail': 'This promotion is no longer available.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        rule = promotion.rule
        
        return Response({
            'promotion': PromotionSerializer(promotion).data,
            'discount_type': rule.type,
            'discount_value': str(rule.value),
            'message': f'Promotion {promotion.code} applied successfully.'
        })


class InventoryMovementViewSet(viewsets.ModelViewSet):
    """ViewSet for InventoryMovement model."""
    
    queryset = InventoryMovement.objects.select_related('variant')
    serializer_class = InventoryMovementSerializer
    permission_classes = [permissions.IsAdminUser]
    filterset_fields = ['variant', 'reason']
    ordering_fields = ['created_at']
    
    def perform_create(self, serializer):
        """Update variant stock when creating a movement."""
        movement = serializer.save()
        variant = movement.variant
        variant.stock += movement.change
        variant.save(update_fields=['stock'])


class CartViewSet(viewsets.ModelViewSet):
    """ViewSet for Cart model with custom cart endpoints."""
    
    queryset = Cart.objects.prefetch_related('items__variant')
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter carts to the current user's carts."""
        if self.request.user.is_staff:
            return super().get_queryset()
        try:
            customer = Customer.objects.get(user=self.request.user)
            return super().get_queryset().filter(customer=customer)
        except Customer.DoesNotExist:
            return Cart.objects.none()
    
    def _get_or_create_cart(self, request):
        """Get the current user's open cart or create one."""
        customer, _ = Customer.objects.get_or_create(
            user=request.user,
            defaults={'email': request.user.email, 'name': request.user.get_full_name() or request.user.username}
        )
        # Use select_for_update to prevent race conditions in concurrent requests
        with transaction.atomic():
            cart = Cart.objects.filter(
                customer=customer,
                status=Cart.Status.OPEN
            ).select_for_update().first()
            
            if not cart:
                cart = Cart.objects.create(
                    customer=customer,
                    status=Cart.Status.OPEN
                )
        return cart
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get the current user's active cart."""
        cart = self._get_or_create_cart(request)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], url_path='me/items')
    def add_item(self, request):
        """Add an item to the current user's cart."""
        cart = self._get_or_create_cart(request)
        
        serializer = CartItemCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        variant = get_object_or_404(Variant, id=serializer.validated_data['variant_id'])
        qty = serializer.validated_data['qty']
        
        with transaction.atomic():
            # Lock the variant row to prevent race conditions
            variant = Variant.objects.select_for_update().get(id=variant.id)
            
            # Check if item already in cart
            existing_item = CartItem.objects.filter(cart=cart, variant=variant).first()
            total_qty = qty + (existing_item.qty if existing_item else 0)
            
            # Check stock for total quantity
            if variant.stock < total_qty:
                return Response(
                    {'detail': f'Insufficient stock. Available: {variant.stock}, requested total: {total_qty}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if existing_item:
                existing_item.qty = total_qty
                existing_item.save(update_fields=['qty'])
                cart_item = existing_item
            else:
                cart_item = CartItem.objects.create(
                    cart=cart,
                    variant=variant,
                    qty=qty,
                    price_at_add=variant.effective_price
                )
        
        return Response(CartItemSerializer(cart_item).data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['patch', 'delete'], url_path=r'me/items/(?P<item_id>[^/.]+)')
    def update_item(self, request, item_id=None):
        """Update or delete a cart item."""
        cart = self._get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        
        if request.method == 'DELETE':
            cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        # PATCH
        serializer = CartItemUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        qty = serializer.validated_data['qty']
        
        # Check stock
        if cart_item.variant.stock < qty:
            return Response(
                {'detail': f'Insufficient stock. Available: {cart_item.variant.stock}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cart_item.qty = qty
        cart_item.save(update_fields=['qty'])
        
        return Response(CartItemSerializer(cart_item).data)
    
    @action(detail=False, methods=['post'], url_path='me/apply-promotion')
    def apply_promotion(self, request):
        """Apply a promotion to the current cart."""
        cart = self._get_or_create_cart(request)
        
        serializer = PromotionApplySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        code = serializer.validated_data['code']
        promotion = get_object_or_404(Promotion, code__iexact=code)
        
        if not promotion.is_available:
            return Response(
                {'detail': 'This promotion is no longer available.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        rule = promotion.rule
        subtotal = cart.total
        
        # Calculate discount
        if rule.type == PricingRule.RuleType.PERCENTAGE:
            discount = subtotal * (rule.value / 100)
        else:
            discount = min(rule.value, subtotal)
        
        new_total = subtotal - discount
        
        return Response({
            'cart': CartSerializer(cart).data,
            'promotion': PromotionSerializer(promotion).data,
            'subtotal': str(subtotal),
            'discount': str(discount),
            'total_after_discount': str(new_total),
        })
    
    @action(detail=False, methods=['post'], url_path='me/checkout')
    def checkout(self, request):
        """Create an order from the current cart."""
        cart = self._get_or_create_cart(request)
        
        if not cart.items.exists():
            return Response(
                {'detail': 'Cart is empty.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        shipping_address = serializer.validated_data['shipping_address']
        billing_address = serializer.validated_data.get('billing_address', shipping_address)
        payment_ref = serializer.validated_data.get('payment_ref', '')
        
        with transaction.atomic():
            # Lock all variant rows to prevent race conditions
            cart_items = list(cart.items.select_related('variant').all())
            variant_ids = [item.variant.id for item in cart_items]
            
            # Lock variants and verify stock availability
            locked_variants = {
                v.id: v for v in Variant.objects.select_for_update().filter(id__in=variant_ids)
            }
            
            # Verify stock for all items
            for cart_item in cart_items:
                variant = locked_variants[cart_item.variant.id]
                if variant.stock < cart_item.qty:
                    return Response(
                        {'detail': f'Insufficient stock for {variant.sku}. Available: {variant.stock}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Calculate totals
            subtotal = sum(item.line_total for item in cart_items)
            discount_total = Decimal('0.00')  # Can be enhanced to apply promotions
            shipping_total = Decimal('0.00')  # Can be calculated based on address
            tax_total = Decimal('0.00')  # Can be calculated based on jurisdiction
            grand_total = subtotal - discount_total + shipping_total + tax_total
            
            # Create order
            order = Order.objects.create(
                order_number=f'ORD-{uuid.uuid4().hex[:8].upper()}',
                customer=cart.customer,
                subtotal=subtotal,
                discount_total=discount_total,
                shipping_total=shipping_total,
                tax_total=tax_total,
                grand_total=grand_total,
                payment_ref=payment_ref,
                shipping_address=shipping_address,
                billing_address=billing_address,
            )
            
            # Create order items and update inventory
            for cart_item in cart_items:
                variant = locked_variants[cart_item.variant.id]
                
                OrderItem.objects.create(
                    order=order,
                    variant=variant,
                    qty=cart_item.qty,
                    unit_price=cart_item.price_at_add,
                    line_total=cart_item.line_total,
                )
                
                # Update stock atomically
                variant.stock -= cart_item.qty
                variant.save(update_fields=['stock'])
                
                # Create inventory movement
                InventoryMovement.objects.create(
                    variant=variant,
                    change=-cart_item.qty,
                    reason='sale',
                    metadata={'order_number': order.order_number}
                )
            
            # Mark cart as converted
            cart.status = Cart.Status.CONVERTED
            cart.save(update_fields=['status'])
        
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet for Order model."""
    
    queryset = Order.objects.prefetch_related('items__variant').select_related('customer')
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status']
    ordering_fields = ['created_at', 'grand_total']
    
    def get_queryset(self):
        """Filter orders to the current user's orders for non-admin users."""
        if self.request.user.is_staff:
            return super().get_queryset()
        try:
            customer = Customer.objects.get(user=self.request.user)
            return super().get_queryset().filter(customer=customer)
        except Customer.DoesNotExist:
            return Order.objects.none()
    
    def get_permissions(self):
        """Only admins can create or update orders directly."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return super().get_permissions()
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get the current user's orders."""
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for Review model."""
    
    queryset = Review.objects.select_related('product', 'customer')
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['product', 'rating']
    ordering_fields = ['created_at', 'rating']
    
    def get_permissions(self):
        """Allow anyone to read, authenticated to create, owner/admin to delete."""
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return super().get_permissions()
    
    def perform_destroy(self, instance):
        """Only allow the review owner or admin to delete."""
        if not self.request.user.is_staff:
            if instance.customer and instance.customer.user != self.request.user:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("You can only delete your own reviews.")
        instance.delete()


class AnalyticsSnapshotViewSet(viewsets.ModelViewSet):
    """ViewSet for AnalyticsSnapshot model."""
    
    queryset = AnalyticsSnapshot.objects.all()
    serializer_class = AnalyticsSnapshotSerializer
    permission_classes = [permissions.IsAdminUser]
    filterset_fields = ['metric', 'period']
    ordering_fields = ['created_at', 'value']
    
    @action(detail=False, methods=['get'])
    def metrics(self, request):
        """Get aggregated metrics for dashboard."""
        # Get latest snapshot for each metric
        metrics = {}
        for metric_type in ['visibility', 'conversion_rate', 'engagement', 'revenue']:
            snapshot = AnalyticsSnapshot.objects.filter(metric=metric_type).order_by('-created_at').first()
            if snapshot:
                metrics[metric_type] = {
                    'value': str(snapshot.value),
                    'period': snapshot.period,
                    'breakdown': snapshot.breakdown,
                }
        
        return Response(metrics)
