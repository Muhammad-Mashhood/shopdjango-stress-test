"""
payments/models.py - Payment processing and transaction records
Depends on: accounts.models, orders.models
"""
from django.db import models
from django.utils.translation import ugettext_lazy as _
from six import python_2_unicode_compatible

from accounts.models import UserProfile
from orders.models import Order


@python_2_unicode_compatible
class Payment(models.Model):
    """A payment transaction linked to an order."""
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('processing', _('Processing')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
        ('refunded', _('Refunded')),
        ('partially_refunded', _('Partially Refunded')),
    )
    GATEWAY_CHOICES = (
        ('stripe', _('Stripe')),
        ('paypal', _('PayPal')),
        ('manual', _('Manual')),
    )

    order = models.OneToOneField(Order, related_name='payment')
    user = models.ForeignKey(UserProfile, related_name='payments')
    gateway = models.CharField(max_length=15, choices=GATEWAY_CHOICES)
    gateway_transaction_id = models.CharField(max_length=200, blank=True)
    gateway_response = models.TextField(blank=True)  # Raw JSON from gateway
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('payment')
        ordering = ['-created_at']

    def __str__(self):
        return u'Payment #%s for Order #%s ($%s)' % (self.pk, self.order.order_number, self.amount)


@python_2_unicode_compatible
class Refund(models.Model):
    """A refund issued for a payment."""
    payment = models.ForeignKey(Payment, related_name='refunds')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    gateway_refund_id = models.CharField(max_length=200, blank=True)
    processed_by = models.ForeignKey(UserProfile, related_name='processed_refunds')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('refund')

    def __str__(self):
        return u'Refund $%s for Payment #%s' % (self.amount, self.payment.pk)


@python_2_unicode_compatible
class SavedPaymentMethod(models.Model):
    """Saved tokenized payment method for a user."""
    user = models.ForeignKey(UserProfile, related_name='saved_payment_methods')
    gateway = models.CharField(max_length=15)
    gateway_customer_id = models.CharField(max_length=200)
    gateway_payment_method_id = models.CharField(max_length=200)
    last4 = models.CharField(max_length=4)
    brand = models.CharField(max_length=30)  # Visa, Mastercard, etc.
    exp_month = models.IntegerField()
    exp_year = models.IntegerField()
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('saved payment method')

    def __str__(self):
        return u'%s ending in %s (%s/%s)' % (self.brand, self.last4, self.exp_month, self.exp_year)
