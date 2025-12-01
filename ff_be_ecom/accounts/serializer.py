from rest_framework import serializers
from django.contrib.auth import get_user_model
from customers.models import Customer

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    class Meta:
        model = User
        fields = ('id','username','email','password','first_name','last_name')
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        # create customer object
        Customer.objects.get_or_create(user=user, defaults={'email': user.email or '', 'name': user.get_full_name() or user.username})
        return user