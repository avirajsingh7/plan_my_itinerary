from django.contrib.auth.models import User
from rest_framework import serializers
from .models import User, Itinerary, Activity, LocationDetails, Image
from collections import defaultdict
from typing import Dict, List, Any
from django.utils import timezone


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    Handles user registration and profile data.
    """
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ["id", "email", "password", "first_name", "last_name", "is_active"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data: Dict[str, Any]) -> User:
        """
        Create and return a new User instance, given the validated data.
        """
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
    """
    Serializer for email verification token.
    """
    token = serializers.UUIDField()


class ItineraryRequestSerializer(serializers.Serializer):
    """
    Serializer for itinerary generation request.
    """
    destination = serializers.CharField(max_length=255)
    num_of_days = serializers.IntegerField()
    must_includes = serializers.ListField(child=serializers.CharField(max_length=255))
    start_date = serializers.DateField(format='%Y-%m-%d')
    end_date = serializers.DateField(format='%Y-%m-%d')

    def validate(self, data):
        if data['end_date'] <= data['start_date']:
            raise serializers.ValidationError("End date must be after start date.")
        if data['num_of_days'] != (data['end_date'] - data['start_date']).days + 1:
            raise serializers.ValidationError("Number of days must match the difference between start and end date.")
        if data['start_date'] < timezone.now().date():
            raise serializers.ValidationError("Start date cannot be in the past.")
        return data
    

class LocationDetailsSerializer(serializers.ModelSerializer):
    """
    Serializer for LocationDetails model.
    """
    class Meta:
        model = LocationDetails
        fields = ['id', 'name', 'street1', 'city', 'state', 'country', 'postalcode', 'address_string', 'latitude', 'longitude', 'ranking', 'rating']


class ImageSerializer(serializers.ModelSerializer):
    """
    Serializer for Image model.
    """
    class Meta:
        model = Image
        fields = ['location', 'thumbnail', 'small', 'medium', 'large', 'original']


class ActivitySerializer(serializers.ModelSerializer):
    """
    Serializer for Activity model.
    """
    class Meta:
        model = Activity
        fields = ['name', 'itinerary', 'day', 'time_of_day', 'duration', 'description', 'location']


class ItinerarySerializer(serializers.ModelSerializer):
    """
    Serializer for Itinerary model.
    """
    class Meta:
        model = Itinerary
        fields = ['id', 'user', 'start_date', 'end_date', 'total_days', 'destination', 'image_url', 'name']


class ActivityResponseSerializer(serializers.ModelSerializer):
    """
    Serializer for Activity model with additional place details and images.
    """
    place_details = LocationDetailsSerializer(source='location', read_only=True)
    place_images = ImageSerializer(source='location.image_set', many=True, read_only=True)

    class Meta:
        model = Activity
        fields = ['name', 'itinerary', 'day', 'time_of_day', 'duration', 'description', 'place_details', 'place_images']


class ItineraryResponseSerializer(serializers.ModelSerializer):
    """
    Serializer for Itinerary model with grouped activities.
    """
    activities = serializers.SerializerMethodField()
    
    class Meta:
        model = Itinerary
        fields = ['id', 'user', 'start_date', 'end_date', 'destination', 'image_url', 'name', 'total_days', 'createdAt', 'activities']

    def get_activities(self, obj: Itinerary) -> Dict[int, List[Dict[str, Any]]]:
        """
        Group activities by day for the itinerary.
        """
        activities = Activity.objects.filter(itinerary=obj)
        grouped_activities = defaultdict(list)

        for activity in activities:
            day = int(activity.day)
            grouped_activities[day].append(ActivityResponseSerializer(activity).data)

        return dict(grouped_activities)  # Convert defaultdict to regular dict for serialization

    def to_representation(self, instance: Itinerary) -> Dict[str, Any]:
        """
        Custom representation of the Itinerary instance.
        """
        representation = super().to_representation(instance)
        representation['activities'] = self.get_activities(instance)
        return representation
