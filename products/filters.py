"""
products/filters.py - Django-filter filterset for products
"""
import django_filters
from products.models import Product, Category, Brand


class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(name='price', lookup_expr='lte')
    category = django_filters.CharFilter(name='category__slug', lookup_expr='exact')
    brand = django_filters.CharFilter(name='brand__slug', lookup_expr='exact')
    tag = django_filters.CharFilter(name='tags__slug', lookup_expr='exact')
    on_sale = django_filters.BooleanFilter(name='compare_price', lookup_expr='isnull', exclude=True)
    featured = django_filters.BooleanFilter(name='featured')
    rating_min = django_filters.NumberFilter(name='average_rating', lookup_expr='gte')

    class Meta:
        model = Product
        fields = ['status', 'featured', 'category', 'brand', 'tag']
