from django.contrib import admin
from discounts.models import Discount, DiscountUsage


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'value', 'used_count', 'valid_from', 'valid_until', 'is_active')
    list_filter = ('discount_type', 'is_active')
    search_fields = ('code', 'name')
    filter_horizontal = ('applicable_products', 'applicable_categories')
    raw_id_fields = ('created_by',)


@admin.register(DiscountUsage)
class DiscountUsageAdmin(admin.ModelAdmin):
    list_display = ('discount', 'user', 'used_at', 'order_id')
    raw_id_fields = ('discount', 'user')
