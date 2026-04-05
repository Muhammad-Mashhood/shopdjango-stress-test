"""
accounts/models.py - Custom User model and related models
Django 1.x style
"""
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_text
from django.utils import timezone
from six import python_2_unicode_compatible

from accounts.managers import UserProfileManager


@python_2_unicode_compatible
class UserProfile(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model for ShopDjango.
    Uses email as the unique identifier instead of username.
    """
    email = models.EmailField(_('email address'), unique=True, db_index=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(blank=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserProfileManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-date_joined']

    def __str__(self):
        return force_text(self.email)

    def get_full_name(self):
        return u'%s %s' % (self.first_name, self.last_name)

    def get_short_name(self):
        return self.first_name


@python_2_unicode_compatible
class Address(models.Model):
    """Reusable address model linked to users"""
    ADDRESS_TYPE_CHOICES = (
        ('billing', _('Billing')),
        ('shipping', _('Shipping')),
    )

    user = models.ForeignKey(
        UserProfile,
        related_name='addresses',
        on_delete=models.CASCADE
    )
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPE_CHOICES, default='shipping')
    street_address = models.CharField(max_length=255)
    apartment = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='US')
    zip_code = models.CharField(max_length=20)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('address')
        verbose_name_plural = _('addresses')

    def __str__(self):
        return u'%s - %s, %s' % (self.user.email, self.city, self.country)


@python_2_unicode_compatible
class UserActivity(models.Model):
    """Tracks user login/logout and page view activity"""
    user = models.ForeignKey(
        UserProfile,
        related_name='activities',
        on_delete=models.CASCADE
    )
    action = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.TextField(blank=True)  # JSON stored as text (Django 1.x)

    class Meta:
        verbose_name = _('user activity')
        ordering = ['-timestamp']

    def __str__(self):
        return u'%s - %s' % (self.user.email, self.action)


@python_2_unicode_compatible
class Wishlist(models.Model):
    """User wishlist - references products via string to avoid circular import"""
    user = models.OneToOneField(UserProfile, related_name='wishlist')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('wishlist')

    def __str__(self):
        return u'Wishlist of %s' % self.user.email
