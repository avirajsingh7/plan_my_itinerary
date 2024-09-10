from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from django.db import transaction

from .serializers import UserSerializer, ItinerarySerializer, ItineraryRequestSerializer
from .models import EmailVerificationToken, Itinerary, LocationDetails, Activity, Image
from .services import EmailService, gemini_client, trip_advisor_client


class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Create and save the verification token
        token = EmailVerificationToken.objects.create(user=user)
        
        # Send verification email
        EmailService.send_verification_email(user.email, token.token)
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, token):
        try:
            verification_token = EmailVerificationToken.objects.get(token=token)
            user = verification_token.user
            user.is_active = True
            user.save()
            verification_token.delete()
            return Response({"detail": "Email successfully verified."}, status=status.HTTP_200_OK)
        except EmailVerificationToken.DoesNotExist:
            return Response({"detail": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)


class GenerateItineraryView(APIView):
    @transaction.atomic
    def post(self, request):
        query_params = request.query_params.copy()
        must_includes = request.query_params.get('must_includes', '').split(',')
        query_params.setlist('must_includes', must_includes)
        serializer = ItineraryRequestSerializer(data=query_params)

        if serializer.is_valid():
            destination = serializer.validated_data['destination']
            num_of_days = serializer.validated_data['num_of_days']
            must_includes = serializer.validated_data['must_includes']
            start_date = serializer.validated_data['start_date']
            end_date = serializer.validated_data['end_date']

            # Generate itinerary using Gemini API
            itinerary_data = gemini_client.get_places_to_visit(destination, num_of_days, must_includes)

            # Create Itinerary instance
            itinerary = Itinerary.objects.create(
                user=request.user,
                start_date=start_date,
                end_date=end_date,
                total_days=num_of_days
            )

            # Process each activity in the generated itinerary
            for activity in itinerary_data['itinerary']:
                place_id = trip_advisor_client.get_tourist_place_id(activity['place_name'], destination)
                if place_id:
                    location, created = LocationDetails.objects.get_or_create(id=place_id)
                    
                    if created:
                        location_details = trip_advisor_client.get_place_details(place_id)
                        if location_details:
                            for key, value in location_details.items():
                                setattr(location, key, value)
                            location.save()

                    Activity.objects.create(
                        itinerary=itinerary,
                        description=activity['description'],
                        location=location,
                        duration=activity['duration'],
                        day=activity['day_number'],
                        time_of_day=activity['time_of_day']
                    )

                    # Fetch and save images only if they don't exist
                    if not Image.objects.filter(location=location).exists():
                        images = trip_advisor_client.get_place_images(place_id)
                        if images:
                            for image_data in images:
                                Image.objects.create(location=location, **image_data)

            # Serialize the created itinerary with all activities and related data
            itinerary_serializer = ItinerarySerializer(itinerary)
            print("Activities:", Activity.objects.filter(itinerary=itinerary))
            return Response({
                "message": "Itinerary created and saved successfully!",
                "data": itinerary_serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            

class RecentItinerariesView(APIView):
    def get(self, request):
        n_itinerary = request.query_params.get('n_itinerary', 4)
        try:
            n_itinerary = int(n_itinerary)
        except ValueError:
            return Response({"error": "Invalid value for 'n'"}, status=status.HTTP_400_BAD_REQUEST)

        recent_itineraries = Itinerary.objects.filter(user=request.user).order_by('-createdAt')[:n_itinerary]
        serializer = ItinerarySerializer(recent_itineraries, many=True)

        return Response({
            "message": f"Retrieved {len(serializer.data)} recent itineraries",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
