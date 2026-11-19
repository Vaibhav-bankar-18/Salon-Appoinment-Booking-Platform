from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email", "phone", "role"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "password", "first_name", "email", "phone"]

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, data):
        # Public sign-up always creates a customer. Staff/admin are created by an admin.
        return User.objects.create_user(role=User.Role.CUSTOMER, **data)
