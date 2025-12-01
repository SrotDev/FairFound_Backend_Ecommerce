from rest_framework import serializers

from rest_framework import serializers
from .models import (
    Category
)
from django.contrib.auth import get_user_model

User = get_user_model()

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'