from django.urls import path
from .views.user import (
    CreateUserView,
    VerifyEmailView,
    UserProfileView,
)
from .views.itineraries import (
    GenerateItineraryView,
    RecentItinerariesView,
    ItineraryDetailView
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    # User-related endpoints
    path("user/register/", CreateUserView.as_view(), name="register"),
    path("user/profile/", UserProfileView.as_view(), name="profile"),
    path("user/verify-email/<uuid:token>/", VerifyEmailView.as_view(), name="verify_email"),

    # Authentication endpoints
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Itinerary-related endpoints
    path("itinerary/generate/", GenerateItineraryView.as_view(), name="generate_itinerary"),
    path("itinerary/recent/", RecentItinerariesView.as_view(), name="recent_itineraries"),
    path("itinerary/<int:itinerary_id>/", ItineraryDetailView.as_view(), name="itinerary_detail"),
]