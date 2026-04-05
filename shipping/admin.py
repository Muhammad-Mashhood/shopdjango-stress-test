from django.contrib import admin
from shipping.models import ShippingZone, ShippingRate, Shipment


class ShippingRateInline(admin.TabularInline):
    model = ShippingRate
    extra = 1


@admin.register(ShippingZone)
class ShippingZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    inlines = [ShippingRateInline]


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_id', 'tracking_number', 'carrier', 'status', 'created_at')
    list_filter = ('status', 'carrier')
    search_fields = ('tracking_number', 'order_id')
    readonly_fields = ('created_at',)
