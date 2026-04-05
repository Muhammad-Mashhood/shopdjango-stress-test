from django.contrib import admin
from inventory.models import StockLevel, StockMovement, Warehouse


@admin.register(StockLevel)
class StockLevelAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'reserved_quantity', 'reorder_threshold')
    list_filter = ('updated_at',)
    search_fields = ('product__name', 'product__sku')
    raw_id_fields = ('product',)


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('product', 'movement_type', 'quantity', 'reference', 'created_at')
    list_filter = ('movement_type', 'created_at')
    search_fields = ('product__name', 'reference')
    readonly_fields = ('created_at',)


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active')
    search_fields = ('name', 'code')
