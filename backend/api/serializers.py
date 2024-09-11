from django.contrib.auth.models import User
from rest_framework import serializers
from .models import User, Itinerary, Activity, LocationDetails, Image
from collections import defaultdict


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
        fields = ['name','itinerary', 'day', 'time_of_day', 'duration', 'description','location']

class ItinerarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Itinerary
        fields = ['user', 'start_date', 'end_date', 'total_days','destination','image_url','name']

class ActivityResponseSerializer(serializers.ModelSerializer):
    place_details = LocationDetailsSerializer(source='location', read_only=True)
    place_images = ImageSerializer(source='location.image_set', many=True, read_only=True)

    class Meta:
        model = Activity
        fields = ['name','itinerary','day', 'time_of_day', 'duration', 'description', 'place_details','place_images']


class ItineraryResponseSerializer(serializers.ModelSerializer):
    activities_by_day = serializers.SerializerMethodField()

    class Meta:
        model = Itinerary
        fields = ['id', 'user', 'start_date', 'end_date', 'destination', 'image_url', 'name', 'total_days', 'createdAt', 'activities_by_day']

    def get_activities_by_day(self, obj):
        # Group activities by day
        activities = Activity.objects.filter(itinerary=obj)
        grouped_activities = defaultdict(list)

        for activity in activities:
            day = int(activity.day)
            grouped_activities[day].append(ActivityResponseSerializer(activity).data)

        return grouped_activities

    def to_representation(self, instance):

        representation = super().to_representation(instance)
        representation['activities'] = self.get_activities_by_day(instance)
        return representation
