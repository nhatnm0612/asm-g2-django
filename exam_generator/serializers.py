from rest_framework import serializers
from user.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "password", "email", "role"]  # Add 'role' to fields
        # extra_kwargs = {'password': {'write_only': True}}
