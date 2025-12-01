from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import (
    AnalyticsSnapshotViewSet
)
router = DefaultRouter()
router.register(r'analytics', AnalyticsSnapshotViewSet, basename='analytics')
urlpatterns = [
    path('', include(router.urls)),
]