"""
inventory/models.py - Stock/inventory management
Depends on: products.models
"""
from django.db import models
from django.utils.translation import ugettext_lazy as _
from six import python_2_unicode_compatible

from products.models import Product, ProductVariant


@python_2_unicode_compatible
class StockLevel(models.Model):
    """Tracks stock quantity for each product."""
    product = models.OneToOneField(Product, related_name='stock')
    quantity = models.IntegerField(default=0)
    reserved_quantity = models.IntegerField(default=0)
    reorder_threshold = models.IntegerField(default=10)
    reorder_quantity = models.IntegerField(default=50)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('stock level')

    def __str__(self):
        return u'%s: %d units' % (self.product.name, self.quantity)

    @property
    def available_quantity(self):
        return self.quantity - self.reserved_quantity

    def is_low_stock(self):
        return self.available_quantity <= self.reorder_threshold


@python_2_unicode_compatible
class VariantStockLevel(models.Model):
    """Tracks stock for product variants."""
    variant = models.OneToOneField(ProductVariant, related_name='stock')
    quantity = models.IntegerField(default=0)
    reserved_quantity = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def available_quantity(self):
        return self.quantity - self.reserved_quantity

    def __str__(self):
        return u'%s: %d units' % (self.variant.name, self.quantity)


@python_2_unicode_compatible
class StockMovement(models.Model):
    """Audit log of all stock quantity changes."""
    MOVEMENT_TYPES = (
        ('in', _('Stock In')),
        ('out', _('Stock Out')),
        ('reserved', _('Reserved')),
        ('released', _('Released')),
        ('adjustment', _('Adjustment')),
    )
    product = models.ForeignKey(Product, related_name='stock_movements')
    movement_type = models.CharField(max_length=15, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField()
    reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('stock movement')
        ordering = ['-created_at']

    def __str__(self):
        return u'%s %s: %d' % (self.product.name, self.movement_type, self.quantity)


@python_2_unicode_compatible
class Warehouse(models.Model):
    """Physical warehouse location."""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    address = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return u'%s (%s)' % (self.name, self.code)
