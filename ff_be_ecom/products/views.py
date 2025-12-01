from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product
from .serializer import ProductSerializer, VariantSerializer
# Create your models here.
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.prefetch_related('variants').all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category','status']
    search_fields = ['name','summary','description','slug']
    ordering_fields = ['created_at','name']
    permission_classes = [AllowAny]
    def get_permissions(self):
        if self.action in ['create','update','partial_update','destroy']:
            return [IsAdminUser()]
        return [AllowAny()]

    @action(detail=True, methods=['get'], url_path='variants')
    def list_variants(self, request, pk=None):
        prod = self.get_object()
        serializer = VariantSerializer(prod.variants.all(), many=True)
        return Response(serializer.data)