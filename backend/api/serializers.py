from django.contrib.auth.models import User
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ["id", "email", "password", "first_name", "last_name","is_active"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            is_active=False  # User starts as inactive
        )
        return user


class ItineraryRequestSerializer(serializers.Serializer):
    destination = serializers.CharField(max_length=255)
    num_of_days = serializers.IntegerField()
    must_includes = serializers.ListField(child=serializers.CharField(max_length=255))

class EmailVerificationSerializer(serializers.Serializer):
    token = serializers.UUIDField()
