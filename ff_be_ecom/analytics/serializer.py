from .models import AnalyticsSnapshot
from rest_framework import serializers
# Create your views here.

class AnalyticsSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalyticsSnapshot
        fields = '__all__'