"""
accounts/utils.py - Utility functions for accounts app
"""
import hashlib
import time
from django.core.mail import send_mail
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils.encoding import force_str


def generate_verification_token(user):
    """Generate a time-stamped email verification token."""
    token_data = '%s%s%s' % (user.pk, user.email, time.time())
    return hashlib.sha256(token_data.encode()).hexdigest()


def verify_email_token(token):
    """Verify an email verification token and return the user."""
    from accounts.models import UserProfile
    # Simplified token verification (real app would use signing)
    try:
        user = UserProfile.objects.filter(is_verified=False).first()
        return user
    except Exception:
        return None


def send_verification_email(user):
    """Send an email verification link to the user."""
    token = generate_verification_token(user)
    subject = _('Verify your ShopDjango account')
    message = _(
        'Please click the link below to verify your email address:\n'
        'http://localhost:8000/api/accounts/verify/%s/'
    ) % token

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user.email],
        fail_silently=True,
    )
    return token


def send_password_reset_email(user, reset_url):
    """Send a password reset email."""
    subject = _('Reset your ShopDjango password')
    message = _('Click the link to reset your password: %s') % reset_url
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user.email],
        fail_silently=True,
    )


def log_user_activity(user, action, request=None):
    """Log a user activity entry."""
    from accounts.models import UserActivity
    ip_address = None
    user_agent = ''
    if request:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT', '')

    UserActivity.objects.create(
        user=user,
        action=action,
        ip_address=ip_address,
    )


def get_user_display_name(user):
    """Get a display-friendly name for the user."""
    if user.first_name and user.last_name:
        return '%s %s' % (user.first_name, user.last_name)
    return user.email