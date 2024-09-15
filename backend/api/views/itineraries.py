from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
from rest_framework.request import Request
from typing import Dict, Any, List, Optional

from ..serializers import (
    ItinerarySerializer,
    ItineraryRequestSerializer,
    ImageSerializer,
    ActivitySerializer,
    LocationDetailsSerializer,
    ItineraryResponseSerializer
)
from ..models import Itinerary, LocationDetails, Image
from ..services import gemini_client, trip_advisor_client


class GenerateItineraryView(APIView):
    """
    View for generating and saving itineraries.
    
    Terms:
    - Itinerary: Represents the overall trip plan, which includes multiple activities..
    - Activity: A single activity in the itinerary, like visiting a place at a specific time.
    - Location: A place visited during the trip.
    - Image: Photo of a location.
    """

    @transaction.atomic
    def post(self, request: Request) -> Response:
        """
        Generate and save an itinerary based on user input.

        Args:
            request: The HTTP request object containing itinerary parameters.

        Returns:
            Response: HTTP response with generated itinerary data or error message.
        """
        validated_request = self._validate_request(request.data)
        if not validated_request.is_valid():
            return Response(validated_request.errors, status=status.HTTP_400_BAD_REQUEST)

        itinerary_params = validated_request.validated_data
        # This is where the itinerary is generated
        generated_itinerary = self._generate_itinerary(itinerary_params)
        
        if generated_itinerary is None:
            return Response({"message": "Failed to generate itinerary"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        created_itinerary = self._create_itinerary(request.user, itinerary_params)
        self._process_activities(created_itinerary, generated_itinerary, itinerary_params['destination'])
        return self._create_response(created_itinerary)

    def _validate_request(self, request_data: Dict[str, Any]) -> ItineraryRequestSerializer:
        """Validate the incoming request data."""
        return ItineraryRequestSerializer(data=request_data)

    def _generate_itinerary(self, itinerary_params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate itinerary data using the Gemini API client."""
        return gemini_client.get_places_to_visit(
            itinerary_params['destination'],
            itinerary_params['num_of_days'],
            itinerary_params['must_includes']
        )

    def _create_itinerary(self, user: User, itinerary_params: Dict[str, Any]) -> Itinerary:
        """Create and save a new Itinerary instance."""
        itinerary_data = {
            'user': user.id,
            'start_date': itinerary_params['start_date'],
            'end_date': itinerary_params['end_date'],
            'total_days': itinerary_params['num_of_days'],
            'destination': itinerary_params['destination'],
            'image_url': None,
            'name': (
                itinerary_params['destination'].split(',')[0] +
                ' Itinerary for ' +
                str(itinerary_params['num_of_days']) +
                ' days'
            )
        }
        serializer = ItinerarySerializer(data=itinerary_data)
        if serializer.is_valid():
            return serializer.save()
        else:
            raise Exception(serializer.errors)

    def _process_activities(self, itinerary: Itinerary, generated_itinerary: Dict[str, Any], destination: str) -> None:
        """Process and save activities for the itinerary."""
        for activity in generated_itinerary['itinerary']:
            place_id = trip_advisor_client.get_tourist_place_id(activity['place_name'], destination)
            if place_id:
                self._get_or_create_location(place_id)
                self._create_activity(itinerary, activity, place_id)
                images = self._fetch_and_save_images(place_id)
                if images and not itinerary.image_url:
                    for image in images:
                        itinerary.image_url = image['original']
                        itinerary.save()
                        break

    def _get_or_create_location(self, place_id: str) -> LocationDetails:
        """Get or create a LocationDetails instance for the given place_id."""
        try:
            return LocationDetails.objects.get(id=place_id)
        except LocationDetails.DoesNotExist:
            location_data = trip_advisor_client.get_place_details(place_id)
            if location_data:
                serializer = LocationDetailsSerializer(data=location_data)
                if serializer.is_valid():
                    return serializer.save()
                else:
                    raise Exception(serializer.errors)
            else:
                raise Exception(f"Could not fetch details for place_id: {place_id}")

    def _create_activity(self, itinerary: Itinerary, activity_data: Dict[str, Any], place_id: str) -> ActivitySerializer:
        """Create and save an Activity instance."""
        activity_data = {
            'name': activity_data['place_name'],
            'itinerary': itinerary.id,
            'description': activity_data['description'],
            'location': int(place_id),
            'duration': activity_data['duration'],
            'day': activity_data['day_number'],
            'time_of_day': activity_data['time_of_day']
        }
        serializer = ActivitySerializer(data=activity_data)
        if serializer.is_valid():
            return serializer.save()
        else:
            raise Exception(serializer.errors)

    def _fetch_and_save_images(self, place_id: str) -> Optional[List[Dict[str, Any]]]:
        """Fetch and save images for a given place_id."""
        # Try to get the images from the database
        existing_images = Image.objects.filter(location_id=place_id)
        if existing_images.exists():
            # Return the serialized images if found
            return ImageSerializer(existing_images, many=True).data

        # Fetch images from TripAdvisor if not in the database
        images = trip_advisor_client.get_place_images(place_id)
        if images:
            # Serialize and save the fetched images
            serializer = ImageSerializer(data=images, many=True)
            if serializer.is_valid():
                serializer.save()  # Save the images to the database
                return serializer.data  # Return the serialized data
            else:
                # Raise an exception if the data is invalid
                raise Exception(serializer.errors)

        return None

    def _create_response(self, itinerary: Itinerary) -> Response:
        """Create the HTTP response for the generated itinerary."""
        itinerary_serializer = ItineraryResponseSerializer(itinerary)
        return Response({
            "message": "Itinerary created and saved successfully!",
            "data": itinerary_serializer.data
        }, status=status.HTTP_201_CREATED)


class RecentItinerariesView(APIView):
    """View for retrieving recent itineraries for a user."""

    def get(self, request: Request) -> Response:
        """
        Retrieve recent itineraries for the authenticated user.

        Args:
            request: The HTTP request object.

        Returns:
            Response: HTTP response with recent itineraries data or error message.
        """
        try:
            num_of_itinerary = request.query_params.get('num_of_itinerary', 5)
            try:
                num_of_itinerary = int(num_of_itinerary)
                if num_of_itinerary <= 0:
                    raise ValueError("Number of itineraries must be positive")
            except ValueError as e:
                return Response({"error": f"Invalid value for 'num_of_itinerary': {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

            recent_itineraries = Itinerary.objects.filter(user=request.user).order_by('-createdAt')[:num_of_itinerary]
            serializer = ItinerarySerializer(recent_itineraries, many=True)

            return Response({
                "message": f"Retrieved {len(serializer.data)} recent itineraries",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ItineraryDetailView(APIView):
    """View for retrieving details of a specific itinerary."""

    def get(self, request: Request, itinerary_id: int) -> Response:
        """
        Retrieve details for a specific itinerary.

        Args:
            request: The HTTP request object.
            itinerary_id (int): The ID of the itinerary to retrieve.

        Returns:
            Response: HTTP response with itinerary details or error message.
        """
        try:
            itinerary = Itinerary.objects.get(id=itinerary_id)
            serializer = ItineraryResponseSerializer(itinerary)
            return Response({
                "message": "Itinerary details retrieved successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Itinerary.DoesNotExist:
            return Response({"message": "Itinerary not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
