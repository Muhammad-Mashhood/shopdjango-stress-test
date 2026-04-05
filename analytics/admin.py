from django.contrib import admin
from analytics.models import SalesReport, ProductPerformance, ProductView, SearchQuery


@admin.register(SalesReport)
class SalesReportAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_orders', 'total_revenue', 'average_order_value')
    ordering = ('-date',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ProductPerformance)
class ProductPerformanceAdmin(admin.ModelAdmin):
    list_display = ('product', 'week_start', 'views', 'purchase_count', 'revenue')
    raw_id_fields = ('product',)
