"""
accounts/backends.py - Custom authentication backends
"""
from django.contrib.auth.backends import ModelBackend
from django.utils.translation import gettext_lazy as _

from accounts.models import UserProfile


class EmailBackend(ModelBackend):
    """
    Authenticate using email address instead of username.
    Django 5.x custom authentication backend.
    """

    def authenticate(self, email=None, password=None, **kwargs):
        try:
            user = UserProfile.objects.get(email=email)
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        except UserProfile.DoesNotExist:
            # Run the default password hasher once to reduce timing
            UserProfile().set_password(password)
            return None

    def get_user(self, user_id):
        try:
            return UserProfile.objects.get(pk=user_id)
        except UserProfile.DoesNotExist:
            return None

    def user_can_authenticate(self, user):
        """Reject inactive users."""
        is_active = getattr(user, 'is_active', None)
        return is_active or is_active is None