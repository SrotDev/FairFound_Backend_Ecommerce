from  rest_framework import serializers
from .models import Cart, CartItem
from .serializer import VariantSerializer
from variants.models import Variant

class CartItemSerializer(serializers.ModelSerializer):
    variant = VariantSerializer(read_only=True)
    variant_id = serializers.PrimaryKeyRelatedField(queryset=Variant.objects.all(), source='variant', write_only=True)
    class Meta:
        model = CartItem
        fields = ['id','cart','variant','variant_id','qty','price_at_add']
        read_only_fields = ['cart','price_at_add','variant']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    class Meta:
        model = Cart
        fields = ['id','customer','status','created_at','updated_at','items']