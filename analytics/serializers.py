"""
analytics/serializers.py - DRF serializers for analytics
"""
from rest_framework import serializers
from analytics.models import SalesReport, ProductPerformance, SearchQuery


class SalesReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesReport
        fields = ('id', 'date', 'total_orders', 'total_revenue', 'total_items_sold',
                  'new_customers', 'returning_customers', 'average_order_value')


class ProductPerformanceSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = ProductPerformance
        fields = ('id', 'product_name', 'week_start', 'views',
                  'add_to_cart_count', 'purchase_count', 'revenue', 'conversion_rate')


class SearchQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchQuery
        fields = ('id', 'query', 'results_count', 'searched_at')
