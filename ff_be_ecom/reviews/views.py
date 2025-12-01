from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from .models import Review
from .serializer import ReviewSerializer
from .models import Customer
# Create your views here.
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related('product','customer').all()
    serializer_class = ReviewSerializer
    def get_permissions(self):
        if self.action in ['destroy']:
            return [IsAdminUser()]
        if self.action in ['create']:
            return [IsAuthenticated()]
        return [AllowAny()]

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        customer, _ = Customer.objects.get_or_create(user=request.user, defaults={'email':request.user.email or '', 'name':request.user.get_full_name() or request.user.username})
        data['customer'] = str(customer.id)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)