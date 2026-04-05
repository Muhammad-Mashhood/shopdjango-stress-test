"""
accounts/signals.py - Signal handlers for accounts app
"""
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from accounts.models import UserProfile, Wishlist


@receiver(post_save, sender=UserProfile)
def create_user_wishlist(sender, instance, created, **kwargs):
    """Automatically create a wishlist when a new user registers."""
    if created:
        Wishlist.objects.create(user=instance)


@receiver(post_save, sender=UserProfile)
def log_profile_changes(sender, instance, created, **kwargs):
    """Log when a user profile is created or updated."""
    if not created:
        from accounts.models import UserActivity
        UserActivity.objects.create(
            user=instance,
            action='profile_saved',
            metadata='{"source": "signal"}'
        )


@receiver(pre_save, sender=UserProfile)
def normalize_email(sender, instance, **kwargs):
    """Normalize email to lowercase before saving."""
    if instance.email:
        instance.email = instance.email.lower()


@receiver(post_delete, sender=UserProfile)
def cleanup_user_data(sender, instance, **kwargs):
    """Clean up associated data when a user is deleted."""
    # Delete avatar file if it exists
    if instance.avatar:
        try:
            instance.avatar.delete(save=False)
        except Exception:
            pass
