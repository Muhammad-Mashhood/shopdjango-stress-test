"""
accounts/views.py - User registration, login, profile management
"""
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_text

from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import UserProfile, Address, UserActivity, Wishlist
from accounts.serializers import (
    UserProfileSerializer, UserRegistrationSerializer,
    AddressSerializer, UserActivitySerializer
)
from accounts.forms import UserRegistrationForm, UserProfileForm
from accounts.utils import send_verification_email, log_user_activity


class UserRegistrationView(APIView):
    """Handle new user registration."""
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            send_verification_email(user)
            log_user_activity(user, 'registered', request)
            return Response(
                {'message': force_text(_('Registration successful. Please check your email.'))},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    """Handle user authentication."""
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(email=email, password=password)
        if user:
            login(request, user)
            log_user_activity(user, 'login', request)
            serializer = UserProfileSerializer(user)
            return Response(serializer.data)
        return Response(
            {'error': force_text(_('Invalid credentials'))},
            status=status.HTTP_401_UNAUTHORIZED
        )


class UserLogoutView(APIView):
    """Handle user logout."""

    def post(self, request):
        log_user_activity(request.user, 'logout', request)
        logout(request)
        return Response({'message': force_text(_('Logged out successfully'))})


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get and update the authenticated user's profile."""
    serializer_class = UserProfileSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def perform_update(self, serializer):
        serializer.save()
        log_user_activity(self.request.user, 'profile_updated', self.request)


class AddressListCreateView(generics.ListCreateAPIView):
    """List and create addresses for authenticated user."""
    serializer_class = AddressSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a specific address."""
    serializer_class = AddressSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)


class UserActivityListView(generics.ListAPIView):
    """List user activity history."""
    serializer_class = UserActivitySerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return UserActivity.objects.filter(user=self.request.user).order_by('-timestamp')[:50]


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
    """Change user password."""
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')

    if not request.user.check_password(old_password):
        return Response(
            {'error': force_text(_('Old password is incorrect'))},
            status=status.HTTP_400_BAD_REQUEST
        )
    request.user.set_password(new_password)
    request.user.save()
    log_user_activity(request.user, 'password_changed', request)
    return Response({'message': force_text(_('Password changed successfully'))})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def verify_email(request, token):
    """Verify user email with token."""
    from accounts.utils import verify_email_token
    user = verify_email_token(token)
    if user:
        user.is_verified = True
        user.save()
        log_user_activity(user, 'email_verified', request)
        return Response({'message': force_text(_('Email verified successfully'))})
    return Response(
        {'error': force_text(_('Invalid or expired token'))},
        status=status.HTTP_400_BAD_REQUEST
    )
