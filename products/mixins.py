"""
products/mixins.py - Reusable mixins for product views
"""
from rest_framework import permissions
from products.models import Product


class ProductOwnerMixin(object):
    """Mixin to restrict product editing to the product creator or admin."""

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def check_product_ownership(self, product):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return True
        return product.created_by == user


class ProductSlugMixin(object):
    """Mixin to add slug-based lookups."""
    lookup_field = 'slug'

    def get_queryset(self):
        return Product.objects.filter(status='active')
