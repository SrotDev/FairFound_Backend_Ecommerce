from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from decimal import Decimal
from promotions.models import Promotion
from promotions.serializer import PromotionSerializer
from variants.models import Variant
# Create your views here.
class PromotionViewSet(viewsets.ModelViewSet):
    queryset = Promotion.objects.select_related('rule').all()
    serializer_class = PromotionSerializer
    def get_permissions(self):
        if self.action in ['create','update','partial_update','destroy']:
            return [IsAuthenticated()]
        return [AllowAny()]

    @action(detail=False, methods=['post'], permission_classes=[AllowAny], url_path='apply')
    def apply_promotion(self, request):
        """
        Preview price impact of promotion.
        Accepts payload: { "code": "PROMO10", "items": [{"variant_id": "<uuid>", "qty": 2}, ...] }
        Returns preview totals (subtotal, discount, grand_total)
        """
        data = request.data
        code = data.get('code')
        items = data.get('items', [])
        promo = Promotion.objects.filter(code__iexact=code, active=True).select_related('rule').first()
        if not promo or not promo.rule.is_active():
            return Response({"detail":"Promotion not found or inactive."}, status=status.HTTP_400_BAD_REQUEST)
        subtotal = Decimal('0.00')
        for it in items:
            vid = it.get('variant_id')
            qty = int(it.get('qty', 1))
            try:
                variant = Variant.objects.get(pk=vid)
            except Variant.DoesNotExist:
                continue
            price = variant.sale_price if variant.sale_price is not None else variant.price
            subtotal += price * qty
        # apply rule
        rule = promo.rule
        discount = Decimal('0.00')
        if rule.type == 'fixed':
            discount = min(Decimal(rule.value), subtotal)
        else:
            discount = (subtotal * (Decimal(rule.value) / Decimal('100.0'))).quantize(Decimal('0.01'))
        grand = subtotal - discount
        return Response({
            "subtotal": subtotal,
            "discount": discount,
            "grand_total": grand,
            "promotion": PromotionSerializer(promo).data
        })