from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from django.db.utils import IntegrityError
from rest_framework.request import Request

from ..serializers import UserSerializer
from ..models import EmailVerificationToken
from ..services import email_service


class CreateUserView(generics.CreateAPIView):
    """View for creating a new user account."""
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request: Request) -> Response:
        """
        Create a new user account and send a verification email.

        Args:
            request: The HTTP request object.

        Returns:
            Response: HTTP response with user data or error message.
        """
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
    """View for retrieving user profile information."""

    def get(self, request: Request) -> Response:
        """
        Retrieve the profile information for the authenticated user.

        Args:
            request: The HTTP request object.

        Returns:
            Response: HTTP response with user profile data or error message.
        """
        try:
            user = request.user
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyEmailView(APIView):
    """View for verifying user email addresses."""

    permission_classes = [AllowAny]

    def get(self, request: Request, token: str) -> Response:
        """
        Verify a user's email address using the provided token.

        Args:
            request: The HTTP request object.
            token (str): The verification token.

        Returns:
            Response: HTTP response indicating success or failure of email verification.
        """
        try:
            verification_token = EmailVerificationToken.objects.get(token=token)
            user = verification_token.user
            user.is_active = True
            user.save()
            verification_token.delete()
            return Response({"message": "Email successfully verified."}, status=status.HTTP_200_OK)
        except EmailVerificationToken.DoesNotExist:
            return Response({"message": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)
