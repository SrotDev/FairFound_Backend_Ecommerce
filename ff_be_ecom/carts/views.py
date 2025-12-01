from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction
from decimal import Decimal
import uuid
from carts.models import Cart, CartItem
from carts.serializer import CartSerializer
from customers.models import Customer
from orders.models import Order, OrderItem
from orders.serializer import OrderSerializer
from variants.models import Variant
from inventory.models import InventoryMovement
from promotions.models import Promotion
# Create your views here.
class CartViewSet(viewsets.GenericViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        customer, _ = Customer.objects.get_or_create(user=request.user, defaults={'email':request.user.email or '', 'name':request.user.get_full_name() or request.user.username})
        cart, _ = Cart.objects.get_or_create(customer=customer, status='open')
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='me/items')
    def add_item(self, request):
        """
        payload: { "variant_id": "<uuid>", "qty": 1 }
        """
        customer, _ = Customer.objects.get_or_create(user=request.user, defaults={'email':request.user.email or '', 'name':request.user.get_full_name() or request.user.username})
        cart, _ = Cart.objects.get_or_create(customer=customer, status='open')
        variant_id = request.data.get('variant_id')
        qty = int(request.data.get('qty', 1))
        variant = get_object_or_404(Variant, pk=variant_id)
        item, created = CartItem.objects.get_or_create(cart=cart, variant=variant, defaults={'qty':qty, 'price_at_add': variant.sale_price if variant.sale_price is not None else variant.price})
        if not created:
            item.qty += qty
            item.save()
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['patch'], url_path='me/items/(?P<item_id>[^/.]+)')
    def update_item(self, request, item_id=None):
        customer, _ = Customer.objects.get_or_create(user=request.user, defaults={'email':request.user.email or '', 'name':request.user.get_full_name() or request.user.username})
        cart = get_object_or_404(Cart, customer=customer, status='open')
        item = get_object_or_404(CartItem, pk=item_id, cart=cart)
        qty = int(request.data.get('qty', item.qty))
        if qty <= 0:
            item.delete()
        else:
            item.qty = qty
            item.save()
        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=['delete'], url_path='me/items/(?P<item_id>[^/.]+)')
    def delete_item(self, request, item_id=None):
        customer, _ = Customer.objects.get_or_create(user=request.user, defaults={'email':request.user.email or '', 'name':request.user.get_full_name() or request.user.username})
        cart = get_object_or_404(Cart, customer=customer, status='open')
        item = get_object_or_404(CartItem, pk=item_id, cart=cart)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'], url_path='me/apply-promotion')
    def apply_promotion(self, request):
        code = request.data.get('code')
        cart = get_object_or_404(Cart, customer__user=request.user, status='open')
        items = cart.items.all()
        payload_items = [{"variant_id": str(i.variant.id), "qty": i.qty} for i in items]
        # delegate to PromotionViewSet.apply_promotion logic - replicated here for convenience
        promo = Promotion.objects.filter(code__iexact=code, active=True).select_related('rule').first()
        if not promo or not promo.rule.is_active():
            return Response({"detail":"Promotion not found or inactive."}, status=status.HTTP_400_BAD_REQUEST)
        subtotal = sum((it.variant.sale_price if it.variant.sale_price is not None else it.variant.price) * it.qty for it in items)
        rule = promo.rule
        discount = Decimal('0.00')
        if rule.type == 'fixed':
            discount = min(Decimal(rule.value), subtotal)
        else:
            discount = (Decimal(subtotal) * (Decimal(rule.value) / Decimal('100.0'))).quantize(Decimal('0.01'))
        return Response({"subtotal": subtotal, "discount": discount, "grand_total": subtotal - discount, "promotion": PromotionSerializer(promo).data})

    @action(detail=False, methods=['post'], url_path='me/checkout')
    @transaction.atomic
    def checkout(self, request):
        """
        Simple checkout: converts cart -> order
        payload expects shipping_address, billing_address, payment_ref (optional)
        """
        customer = get_object_or_404(Customer, user=request.user)
        cart = get_object_or_404(Cart, customer=customer, status='open')
        items = cart.items.select_related('variant').all()
        if not items:
            return Response({"detail":"Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)
        # compute totals
        subtotal = Decimal('0.00')
        for it in items:
            price = it.price_at_add
            subtotal += price * it.qty
        discount_total = Decimal('0.00')  # promotions application could be here
        shipping_total = Decimal(request.data.get('shipping_total', '0.00'))
        tax_total = Decimal(request.data.get('tax_total', '0.00'))
        grand_total = subtotal - discount_total + shipping_total + tax_total
        order = Order.objects.create(
            order_number=str(uuid.uuid4()).split('-')[0].upper(),
            customer=customer,
            subtotal=subtotal,
            discount_total=discount_total,
            shipping_total=shipping_total,
            tax_total=tax_total,
            grand_total=grand_total,
            currency='USD',
            payment_ref=request.data.get('payment_ref'),
            shipping_address=request.data.get('shipping_address', {}),
            billing_address=request.data.get('billing_address', {})
        )
        # create order items and decrement stock
        for it in items:
            OrderItem.objects.create(
                order=order,
                variant=it.variant,
                qty=it.qty,
                unit_price=it.price_at_add,
                line_total=(it.price_at_add * it.qty)
            )
            # reduce stock
            it.variant.stock = max(0, it.variant.stock - it.qty)
            it.variant.save()
            # record inventory movement
            InventoryMovement.objects.create(variant=it.variant, change=-it.qty, reason='sale', metadata={'order':str(order.id)})
        cart.status = 'converted'
        cart.save()
        # optionally clear items (we keep history)
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)