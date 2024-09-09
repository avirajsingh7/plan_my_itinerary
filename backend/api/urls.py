from django.contrib import admin
from django.urls import path, include
from .views import CreateUserView, VerifyEmailView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .api.generate_itinerary_api import generate_itinerary


urlpatterns = [
    path("user/register/", CreateUserView.as_view(), name="register"),
    path("user/verify-email/<uuid:token>/", VerifyEmailView.as_view(), name="verify_email"),
    path("token/", TokenObtainPairView.as_view(), name="get_token"),
    path("token/refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("generate_itinerary/", generate_itinerary, name="generate_itinerary"),
]