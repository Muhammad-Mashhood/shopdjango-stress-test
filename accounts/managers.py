"""
accounts/managers.py - Custom UserProfile manager
"""
from django.contrib.auth.models import BaseUserManager
from django.utils.translation import ugettext_lazy as _


class UserProfileManager(BaseUserManager):
    """
    Custom manager for UserProfile model.
    Handles user creation with email as unique identifier.
    """

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)

    def get_verified_users(self):
        """Return only verified users."""
        return self.get_queryset().filter(is_verified=True, is_active=True)

    def get_staff_users(self):
        """Return only staff users."""
        return self.get_queryset().filter(is_staff=True)
