"""
products/utils.py - Utility functions for products app
"""
from django.utils.translation import ugettext_lazy as _
from products.models import Product


def update_product_view_count(product):
    """Increment the view counter for a product."""
    Product.objects.filter(pk=product.pk).update(view_count=product.view_count + 1)


def get_featured_products(limit=8):
    """Return active featured products."""
    return Product.objects.filter(
        status='active', featured=True
    ).select_related('category', 'brand').prefetch_related('images')[:limit]


def update_product_rating(product):
    """Recalculate and update a product's average rating."""
    from reviews.models import Review
    reviews = Review.objects.filter(product=product, is_approved=True)
    count = reviews.count()
    if count > 0:
        total = sum(r.rating for r in reviews)
        avg = round(total / count, 2)
    else:
        avg = 0
    Product.objects.filter(pk=product.pk).update(average_rating=avg, review_count=count)
    return avg


def get_low_stock_products(threshold=10):
    """Return products with stock below the given threshold."""
    from inventory.models import StockLevel
    low_stock_ids = StockLevel.objects.filter(
        quantity__lte=threshold
    ).values_list('product_id', flat=True)
    return Product.objects.filter(pk__in=low_stock_ids, status='active')


def apply_discount_to_product(product, discount):
    """Apply a discount to a product's price."""
    from discounts.models import Discount
    if discount.discount_type == 'percentage':
        discounted = product.price * (1 - discount.value / 100)
    else:
        discounted = product.price - discount.value
    return max(discounted, 0)
