from rest_framework import serializers
from orders.models import Order, OrderItem
from variants.serializer import VariantSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    variant = VariantSerializer(read_only=True)
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = '__all__'