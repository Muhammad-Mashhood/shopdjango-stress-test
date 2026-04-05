"""
orders/models.py - Order management
Depends on: accounts.models, products.models, discounts.models, shipping.models
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.encoding import force_str
from six import python_2_unicode_compatible

from accounts.models import UserProfile, Address
from products.models import Product, ProductVariant
from discounts.models import Discount
from shipping.models import ShippingRate


@python_2_unicode_compatible
class Cart(models.Model):
    """Shopping cart for authenticated users and guests."""
    user = models.OneToOneField(UserProfile, null=True, blank=True, related_name='cart')
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('cart')

    def __str__(self):
        if self.user:
            return u'Cart of %s' % self.user.email
        return u'Guest Cart (%s)' % self.session_key

    def get_total(self):
        return sum(item.get_subtotal() for item in self.items.all())

    def get_item_count(self):
        return self.items.count()


@python_2_unicode_compatible
class CartItem(models.Model):
    """An item in a shopping cart."""
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='cart_items', on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, null=True, blank=True, related_name='cart_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'product', 'variant')

    def __str__(self):
        return u'%dx %s' % (self.quantity, self.product.name)

    def get_subtotal(self):
        if self.variant and self.variant.price:
            return self.variant.price * self.quantity
        return self.product.price * self.quantity


@python_2_unicode_compatible
class Order(models.Model):
    """A confirmed order placed by a user."""
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('confirmed', _('Confirmed')),
        ('processing', _('Processing')),
        ('shipped', _('Shipped')),
        ('delivered', _('Delivered')),
        ('cancelled', _('Cancelled')),
        ('refunded', _('Refunded')),
    )
    PAYMENT_METHOD_CHOICES = (
        ('stripe', _('Credit Card (Stripe)')),
        ('paypal', _('PayPal')),
        ('cod', _('Cash on Delivery')),
    )

    user = models.ForeignKey(UserProfile, related_name='orders', on_delete=models.CASCADE)
    order_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    billing_address = models.ForeignKey(
        Address, related_name='billing_orders', null=True, on_delete=models.SET_NULL
    )
    shipping_address = models.ForeignKey(
        Address, related_name='shipping_orders', null=True, on_delete=models.SET_NULL
    )
    shipping_rate = models.ForeignKey(ShippingRate, null=True, blank=True, on_delete=models.SET_NULL)
    discount = models.ForeignKey(Discount, null=True, blank=True, related_name='orders', on_delete=models.CASCADE)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=15, choices=PAYMENT_METHOD_CHOICES)
    payment_status = models.CharField(max_length=20, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('order')
        ordering = ['-created_at']

    def __str__(self):
        return force_str(u'Order #%s by %s' % (self.order_number, self.user.email))


@python_2_unicode_compatible
class OrderItem(models.Model):
    """A line item in an order (snapshot of product at time of purchase)."""
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, null=True, blank=True, related_name='order_items', on_delete=models.CASCADE)
    product_name = models.CharField(max_length=200)  # Snapshot at time of order
    product_sku = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = _('order item')

    def __str__(self):
        return u'%dx %s (Order #%s)' % (self.quantity, self.product_name, self.order.order_number)
