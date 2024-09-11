from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from django.db import transaction
from django.db.utils import IntegrityError

from .serializers import (
    UserSerializer, ItinerarySerializer, ItineraryRequestSerializer,
    ImageSerializer, ActivitySerializer, LocationDetailsSerializer,
    ItineraryResponseSerializer
)
from .models import EmailVerificationToken, Itinerary, LocationDetails, Image
from .services import email_service, gemini_client, trip_advisor_client


class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            
            # Create and save the verification token
            token = EmailVerificationToken.objects.create(user=user)
            
            # Send verification email
            email_service.send_verification_email(user.email, token.token)
            
            headers = self.get_success_headers(serializer.data)
            response_data = {
                **serializer.data,
                "message": "Registration successful. Please check your email to verify your account."
            }
            return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)
        except IntegrityError as e:
            if 'unique constraint' in str(e).lower():
                return Response({"message": "A user with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"message": "An error occurred while creating the user. Enter valid email and password."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserProfileView(APIView):
    def get(self, request):
        try:
            user = request.user
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, token):
        try:
            verification_token = EmailVerificationToken.objects.get(token=token)
            user = verification_token.user
            user.is_active = True
            user.save()
            verification_token.delete()
            return Response({"message": "Email successfully verified."}, status=status.HTTP_200_OK)
        except EmailVerificationToken.DoesNotExist:
            return Response({"message": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)


class GenerateItineraryView(APIView):
    @transaction.atomic
    def post(self, request):
        serializer = self._validate_request(request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        itinerary_data = self._generate_itinerary(serializer.validated_data)
        
        if itinerary_data is None:
            return Response({"message": "Failed to generate itinerary"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        itinerary = self._create_itinerary(request.user, serializer.validated_data)
        self._process_activities(itinerary, itinerary_data, serializer.validated_data['destination'])
        return self._create_response(itinerary)

    def _validate_request(self, data):
        return ItineraryRequestSerializer(data=data)

    def _generate_itinerary(self, validated_data):
        return gemini_client.get_places_to_visit(
            validated_data['destination'],
            validated_data['num_of_days'],
            validated_data['must_includes']
        )

    def _create_itinerary(self, user, validated_data):
        itinerary_data = {
            'user': user.id,
            'start_date': validated_data['start_date'],
            'end_date': validated_data['end_date'],
            'total_days': validated_data['num_of_days'],
            'destination': validated_data['destination'],
            'image_url': None,
            'name': (
                validated_data['destination'].split(',')[0] +
                ' Itinerary for ' +
                str(validated_data['num_of_days']) +
                ' days'
            )
        }
        serializer = ItinerarySerializer(data=itinerary_data)
        if serializer.is_valid():
            return serializer.save()
        else:
            raise Exception(serializer.errors)

    def _process_activities(self, itinerary, itinerary_data, destination):
        for activity in itinerary_data['itinerary']:
            place_id = trip_advisor_client.get_tourist_place_id(activity['place_name'], destination)
            if place_id:
                location = self._get_or_create_location(place_id)
                self._create_activity(itinerary, activity, place_id)
                images = self._fetch_and_save_images(place_id)
                print("images in view")
                print(images)
                if images and not itinerary.image_url:
                    for image in images:
                        itinerary.image_url = image.original
                        itinerary.save()
                        break

    def _get_or_create_location(self, place_id):
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

    def _create_activity(self, itinerary, activity_data, place_id):
        activity_data = {
            'name': activity_data['place_name'],
            'itinerary': itinerary.id,
            'description': activity_data['description'],
            'location': place_id,
            'duration': activity_data['duration'],
            'day': activity_data['day_number'],
            'time_of_day': activity_data['time_of_day']
        }
        serializer = ActivitySerializer(data=activity_data)
        if serializer.is_valid():
            return serializer.save()
        else:
            raise Exception(serializer.errors)

    def _fetch_and_save_images(self, place_id):
        try:
            return Image.objects.filter(location_id=place_id)
        except Image.DoesNotExist:
            images = trip_advisor_client.get_place_images(place_id)
            if images:
                serializer = ImageSerializer(data=images, many=True)
                if serializer.is_valid():
                    serializer.save()
                    return images
                else:
                    raise Exception(serializer.errors)
        return None

    def _create_response(self, itinerary):
        itinerary_serializer = ItineraryResponseSerializer(itinerary)
        return Response({
            "message": "Itinerary created and saved successfully!",
            "data": itinerary_serializer.data
        }, status=status.HTTP_201_CREATED)


class RecentItinerariesView(APIView):
    def get(self, request):
        try:
            num_of_itinerary = request.data.get('num_of_itinerary', 4)
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
    def get(self, request, itinerary_id):
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
