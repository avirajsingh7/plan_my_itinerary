from django.urls import path
from .views import CreateUserView, VerifyEmailView, GenerateItineraryView, RecentItinerariesView, UserProfileView, ItineraryDetailView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path("user/register/", CreateUserView.as_view(), name="register"),
    path("user/profile/", UserProfileView.as_view(), name="profile"),
    path("user/verify-email/<uuid:token>/", VerifyEmailView.as_view(), name="verify_email"),
    path("token/", TokenObtainPairView.as_view(), name="get_token"),
    path("token/refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("itinerary/generate/", GenerateItineraryView.as_view(), name="generate_itinerary"),
    path("itinerary/recent/", RecentItinerariesView.as_view(), name="recent_itineraries"),
    path("itinerary/<int:itinerary_id>/", ItineraryDetailView.as_view(), name="itinerary_detail"),
]