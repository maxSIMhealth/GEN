from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            # "password",
        )
        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(), fields=["username", "email"]
            )
        ]
