from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.status import HTTP_200_OK
from rest_framework import permissions
from typing import Any
from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import (
    ChangePasswordSerializer,
    RegisterSerializer,
    UserSerializer,
)

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    """POST /api/auth/register/ - public endpoint for new user registration. """

    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

class UserProfileView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /auth/me/ - Fetch or update the authenticated user's profile."""

    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self) -> Any:
        return self.request.user

class ChangePasswordView(generics.GenericAPIView):
    """POST /api/auth/change-password/ - change the current user password. """

    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user

        if not user.check_password(serializer.validated_data["old_password"]):
            return Response(
                {"old_password": ["Wrong password"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(serializer.validated_data["new_password"])
        user.save()
        return Response(
            {"detail": "Password updated successfully."},
            status=status.HTTP_200_OK,
        )

class LogoutView(generics.GenericAPIView):
    """POST /api/auth/logout/ - Blacklist the refresh token to logout. """

    permission_classes = [IsAuthenticated]

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response(
                    {"detail": "Refresh token is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"detail": "Successfully logged out."},
                status=HTTP_200_OK,
            )
        
        except Exception:
            return Response(
                {"detial": "Invalid or expired token."},
                status=HTTP_400_BAD_REQUEST,
            )