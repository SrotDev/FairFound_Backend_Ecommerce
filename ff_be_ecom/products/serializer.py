
from rest_framework import serializers
from products.models import Product
from variants.serializer import VariantSerializer
class ProductSerializer(serializers.ModelSerializer):
    variants = VariantSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = '__all__'