from django.shortcuts import render
from .models import AnalyticsSnapshot
from .serializer import AnalyticsSnapshotSerializer
from rest_framework import viewsets 
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend


class AnalyticsSnapshotViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AnalyticsSnapshot.objects.all()
    serializer_class = AnalyticsSnapshotSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['metric','period']