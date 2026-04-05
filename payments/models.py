"""
payments/models.py - Payment processing and transaction records
Depends on: accounts.models, orders.models
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import UniqueConstraint, Index

from accounts.models import UserProfile
from orders.models import Order


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

    order = models.OneToOneField(Order, related_name='payment', on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, related_name='payments', on_delete=models.CASCADE)
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
        constraints = [
            UniqueConstraint(fields=['order'], name='unique_payment_per_order')
        ]

    def __str__(self):
        return f'Payment #{self.pk} for Order #{self.order.order_number} (${self.amount})'


class Refund(models.Model):
    """A refund issued for a payment."""
    payment = models.ForeignKey(Payment, related_name='refunds', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    gateway_refund_id = models.CharField(max_length=200, blank=True)
    processed_by = models.ForeignKey(UserProfile, related_name='processed_refunds', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('refund')

    def __str__(self):
        return f'Refund ${self.amount} for Payment #{self.payment.pk}'


class SavedPaymentMethod(models.Model):
    """Saved tokenized payment method for a user."""
    user = models.ForeignKey(UserProfile, related_name='saved_payment_methods', on_delete=models.CASCADE)
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
        indexes = [
            Index(fields=['user', 'gateway'], name='saved_payment_method_index')
        ]

    def __str__(self):
        return f'{self.brand} ending in {self.last4} ({self.exp_month}/{self.exp_year})'