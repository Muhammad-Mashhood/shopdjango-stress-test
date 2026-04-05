"""
shipping/models.py - Shipping zones, rates, and shipment tracking
Depends on: accounts.models, orders (via FK string)
"""
from django.db import models
from django.utils.translation import ugettext_lazy as _
from six import python_2_unicode_compatible

from accounts.models import UserProfile, Address


@python_2_unicode_compatible
class ShippingZone(models.Model):
    """A geographic zone used to define shipping rates."""
    name = models.CharField(max_length=100)
    countries = models.TextField()  # Comma-separated country codes
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return u'%s' % self.name

    def get_countries_list(self):
        return [c.strip() for c in self.countries.split(',')]


@python_2_unicode_compatible
class ShippingRate(models.Model):
    """Shipping rate for a zone and method."""
    SHIPPING_METHOD_CHOICES = (
        ('standard', _('Standard Shipping')),
        ('express', _('Express Shipping')),
        ('overnight', _('Overnight Shipping')),
        ('free', _('Free Shipping')),
    )
    zone = models.ForeignKey(ShippingZone, related_name='rates')
    method = models.CharField(max_length=20, choices=SHIPPING_METHOD_CHOICES)
    min_weight = models.DecimalField(max_digits=8, decimal_places=3, default=0)
    max_weight = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    estimated_days_min = models.IntegerField(default=3)
    estimated_days_max = models.IntegerField(default=7)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('shipping rate')

    def __str__(self):
        return u'%s - %s: $%s' % (self.zone.name, self.method, self.price)


@python_2_unicode_compatible
class Shipment(models.Model):
    """Tracks a physical shipment."""
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('processing', _('Processing')),
        ('shipped', _('Shipped')),
        ('in_transit', _('In Transit')),
        ('delivered', _('Delivered')),
        ('returned', _('Returned')),
        ('lost', _('Lost')),
    )
    order_id = models.IntegerField()  # Avoids circular import with orders
    shipping_address = models.ForeignKey(Address, null=True, on_delete=models.SET_NULL)
    shipping_rate = models.ForeignKey(ShippingRate, null=True, on_delete=models.SET_NULL)
    tracking_number = models.CharField(max_length=100, unique=True, null=True, blank=True)
    carrier = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    shipped_at = models.DateTimeField(null=True, blank=True)
    estimated_delivery = models.DateField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('shipment')
        ordering = ['-created_at']

    def __str__(self):
        return u'Shipment #%s for Order #%s' % (self.pk, self.order_id)
