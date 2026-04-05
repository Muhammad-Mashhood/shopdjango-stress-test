from django.contrib import admin
from orders.models import Cart, CartItem, Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'product_sku', 'unit_price', 'total_price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'status', 'total', 'payment_status', 'created_at')
    list_filter = ('status', 'payment_status', 'payment_method', 'created_at')
    search_fields = ('order_number', 'user__email')
    readonly_fields = ('order_number', 'subtotal', 'discount_amount', 'shipping_cost', 'tax_amount', 'total')
    inlines = [OrderItemInline]
    raw_id_fields = ('user', 'billing_address', 'shipping_address', 'discount')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_item_count', 'updated_at')
    raw_id_fields = ('user',)
