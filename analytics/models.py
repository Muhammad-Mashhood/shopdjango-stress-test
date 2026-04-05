"""
analytics/models.py - Analytics data models
Depends on: accounts.models, products.models, orders.models
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from six import python_2_unicode_compatible

from accounts.models import UserProfile
from products.models import Product
from orders.models import Order


@python_2_unicode_compatible
class ProductView(models.Model):
    """Tracks each unique product page view."""
    product = models.ForeignKey(Product, related_name='analytics_views', on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, null=True, blank=True, related_name='product_views', on_delete=models.CASCADE)
    session_key = models.CharField(max_length=40, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    referrer = models.URLField(blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('product view')
        ordering = ['-viewed_at']

    def __str__(self):
        return u'View of %s at %s' % (self.product.name, self.viewed_at)


@python_2_unicode_compatible
class SearchQuery(models.Model):
    """Records search queries made by users."""
    user = models.ForeignKey(UserProfile, null=True, blank=True, related_name='search_queries', on_delete=models.CASCADE)
    query = models.CharField(max_length=200)
    results_count = models.IntegerField(default=0)
    clicked_product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.SET_NULL)
    searched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('search query')
        ordering = ['-searched_at']

    def __str__(self):
        return u'Search: "%s" (%d results)' % (self.query, self.results_count)


@python_2_unicode_compatible
class SalesReport(models.Model):
    """Aggregated daily sales data for reporting."""
    date = models.DateField(unique=True)
    total_orders = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_items_sold = models.IntegerField(default=0)
    new_customers = models.IntegerField(default=0)
    returning_customers = models.IntegerField(default=0)
    average_order_value = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('sales report')
        ordering = ['-date']

    def __str__(self):
        return u'Sales Report: %s ($%s)' % (self.date, self.total_revenue)


@python_2_unicode_compatible
class ProductPerformance(models.Model):
    """Weekly product performance snapshot."""
    product = models.ForeignKey(Product, related_name='performance_records', on_delete=models.CASCADE)
    week_start = models.DateField()
    views = models.IntegerField(default=0)
    add_to_cart_count = models.IntegerField(default=0)
    purchase_count = models.IntegerField(default=0)
    revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    conversion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta:
        verbose_name = _('product performance')
        unique_together = ('product', 'week_start')

    def __str__(self):
        return u'%s performance (%s)' % (self.product.name, self.week_start)
