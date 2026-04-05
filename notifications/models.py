"""
notifications/models.py - Notification records for users
Depends on: accounts.models
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import UniqueConstraint, Index

from accounts.models import UserProfile


class Notification(models.Model):
    """An in-app notification for a user."""
    NOTIFICATION_TYPES = (
        ('order_placed', _('Order Placed')),
        ('order_shipped', _('Order Shipped')),
        ('order_delivered', _('Order Delivered')),
        ('order_cancelled', _('Order Cancelled')),
        ('payment_success', _('Payment Successful')),
        ('payment_failed', _('Payment Failed')),
        ('refund_processed', _('Refund Processed')),
        ('review_approved', _('Review Approved')),
        ('low_stock_alert', _('Low Stock Alert')),
        ('price_drop', _('Price Drop Alert')),
        ('new_message', _('New Message')),
        ('account_verified', _('Account Verified')),
    )
    user = models.ForeignKey(UserProfile, related_name='notifications', on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    related_object_id = models.IntegerField(null=True, blank=True)
    related_object_type = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('notification')
        ordering = ['-created_at']
        constraints = [
            # UniqueConstraint(fields=['user', 'notification_type'], name='unique_notification')
        ]
        indexes = [
            # Index(fields=['user'], name='user_index')
        ]

    def __str__(self):
        return f'{self.notification_type} to {self.user.email}: {self.title}'


class EmailLog(models.Model):
    """Log of all outbound emails sent to users."""
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('sent', _('Sent')),
        ('failed', _('Failed')),
        ('bounced', _('Bounced')),
    )
    user = models.ForeignKey(UserProfile, related_name='email_logs', null=True, blank=True, on_delete=models.SET_NULL)
    recipient_email = models.EmailField()
    subject = models.CharField(max_length=200)
    body = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('email log')
        ordering = ['-created_at']

    def __str__(self):
        return f'Email to {self.recipient_email}: {self.subject} ({self.status})'