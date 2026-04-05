"""
discounts/models.py - Coupons and discount rules
Depends on: products.models, accounts.models
"""
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from six import python_2_unicode_compatible

from accounts.models import UserProfile
from products.models import Product, Category


@python_2_unicode_compatible
class Discount(models.Model):
    """A discount rule (percentage or fixed amount)."""
    DISCOUNT_TYPE_CHOICES = (
        ('percentage', _('Percentage')),
        ('fixed', _('Fixed Amount')),
    )
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=15, choices=DISCOUNT_TYPE_CHOICES, default='percentage')
    value = models.DecimalField(max_digits=8, decimal_places=2)
    min_purchase_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    usage_limit = models.IntegerField(null=True, blank=True)
    used_count = models.IntegerField(default=0)
    per_user_limit = models.IntegerField(default=1)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    applicable_products = models.ManyToManyField(Product, blank=True, related_name='discounts')
    applicable_categories = models.ManyToManyField(Category, blank=True, related_name='discounts')
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(UserProfile, related_name='created_discounts')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('discount')
        ordering = ['-created_at']

    def __str__(self):
        return u'%s (%s)' % (self.code, self.get_discount_type_display())

    def is_valid(self):
        """Check if this discount is currently applicable."""
        now = timezone.now()
        return (
            self.is_active and
            self.valid_from <= now <= self.valid_until and
            (self.usage_limit is None or self.used_count < self.usage_limit)
        )

    def calculate_discount(self, amount):
        """Calculate the actual discount amount for a given order total."""
        if self.discount_type == 'percentage':
            discount = amount * (self.value / 100)
        else:
            discount = self.value
        if self.max_discount_amount:
            discount = min(discount, self.max_discount_amount)
        return round(discount, 2)


@python_2_unicode_compatible
class DiscountUsage(models.Model):
    """Tracks which users have used which discounts."""
    discount = models.ForeignKey(Discount, related_name='usages')
    user = models.ForeignKey(UserProfile, related_name='discount_usages')
    used_at = models.DateTimeField(auto_now_add=True)
    order_id = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = _('discount usage')

    def __str__(self):
        return u'%s used by %s' % (self.discount.code, self.user.email)
