from django.contrib.auth.models import User
from rest_framework import serializers
from .models import User, Itinerary, Activity, LocationDetails, Image


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
    

class EmailVerificationSerializer(serializers.Serializer):
    token = serializers.UUIDField()


class ItineraryRequestSerializer(serializers.Serializer):
    destination = serializers.CharField(max_length=255)
    num_of_days = serializers.IntegerField()
    must_includes = serializers.ListField(child=serializers.CharField(max_length=255))
    start_date = serializers.DateField(format='%Y-%m-%d')
    end_date = serializers.DateField(format='%Y-%m-%d')


class LocationDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationDetails
        fields = ['id', 'name', 'street1', 'city', 'state', 'country', 'postalcode', 'address_string', 'latitude', 'longitude', 'ranking', 'rating']


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['location','thumbnail', 'small', 'medium', 'large', 'original']

class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ['itinerary', 'day', 'time_of_day', 'duration', 'description','location']

class ItinerarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Itinerary
        fields = ['user', 'start_date', 'end_date', 'total_days']

class ActivityResponseSerializer(serializers.ModelSerializer):
    place_details = LocationDetailsSerializer(source='location', read_only=True)
    place_images = ImageSerializer(source='location.image_set', many=True, read_only=True)

    class Meta:
        model = Activity
        fields = ['itinerary','day', 'time_of_day', 'duration', 'description', 'place_details','place_images']


class ItineraryResponseSerializer(serializers.ModelSerializer):
    activities = ActivityResponseSerializer(source='activity_set', many=True, read_only=True)

    class Meta:
        model = Itinerary
        fields = ['id', 'user', 'start_date', 'end_date', 'total_days', 'createdAt', 'activities']