from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .serializers import UserSerializer, ItinerarySerializer
from .models import EmailVerificationToken, Itinerary, LocationDetails, Activity, Image
from .services import EmailService
from rest_framework.views import APIView
from django.db import transaction


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
        itinerary_data = request.data.get('itinerary', {})
        activities_data = itinerary_data.get('activities', [])

        itinerary = Itinerary.objects.create(
            user=request.user,
            start_date=itinerary_data.get('start_date'),
            end_date=itinerary_data.get('end_date'),
            total_days=itinerary_data.get('total_days')
        )

        for activity_data in activities_data:
            location_data = activity_data.pop('place_details', {})
            images_data = activity_data.pop('place_images', [])

            location, _ = LocationDetails.objects.get_or_create(
                location_id=location_data.get('location_id'),
                defaults=location_data
            )

            activity = Activity.objects.create(
                itinerary=itinerary,
                location=location,
                **activity_data
            )

            for image_data in images_data:
                Image.objects.create(location=location, **image_data)

        serializer = ItinerarySerializer(itinerary)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


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
