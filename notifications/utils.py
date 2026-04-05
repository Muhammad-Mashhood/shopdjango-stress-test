"""
notifications/utils.py - Notification sending utilities
Depends on: notifications.models, accounts.models, orders.models
"""
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from notifications.models import Notification, EmailLog
from accounts.models import UserProfile


def create_notification(user, notification_type, title, message,
                        related_object_id=None, related_object_type=None):
    """Create an in-app notification for a user."""
    return Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
        related_object_id=related_object_id,
        related_object_type=related_object_type,
    )


def send_email_notification(user, subject, message):
    """Send an email to a user and log it."""
    log = EmailLog.objects.create(
        user=user,
        recipient_email=user.email,
        subject=subject,
        body=message,
        status='pending',
    )
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
        )
        EmailLog.objects.filter(pk=log.pk).update(status='sent', sent_at=timezone.now())
    except Exception as e:
        EmailLog.objects.filter(pk=log.pk).update(status='failed', error_message=str(e))


def send_order_notification(order, notification_type):
    """Send an order-related notification to the user."""
    messages = {
        'order_placed': ('Order Confirmed', 'Your order #%s has been placed successfully.' % order.order_number),
        'order_shipped': ('Order Shipped', 'Your order #%s has been shipped!' % order.order_number),
        'order_delivered': ('Order Delivered', 'Your order #%s has been delivered.' % order.order_number),
        'order_cancelled': ('Order Cancelled', 'Your order #%s has been cancelled.' % order.order_number),
    }
    title, message = messages.get(notification_type, ('Order Update', 'Your order has been updated.'))
    create_notification(order.user, notification_type, title, message,
                        related_object_id=order.pk, related_object_type='order')
    send_email_notification(order.user, title, message)


def send_payment_notification(payment, success=True):
    """Send a payment success/failure notification."""
    if success:
        title = 'Payment Successful'
        message = 'Your payment of $%s has been processed successfully.' % payment.amount
        ntype = 'payment_success'
    else:
        title = 'Payment Failed'
        message = 'Your payment of $%s could not be processed. Please try again.' % payment.amount
        ntype = 'payment_failed'
    create_notification(payment.user, ntype, title, message,
                        related_object_id=payment.pk, related_object_type='payment')
    send_email_notification(payment.user, title, message)


def send_admin_notification(notification_type, title, message):
    """Send a notification to all admin users."""
    admins = UserProfile.objects.filter(is_staff=True, is_active=True)
    for admin in admins:
        create_notification(admin, notification_type, title, message)
