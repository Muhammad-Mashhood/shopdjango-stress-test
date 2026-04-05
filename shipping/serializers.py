from rest_framework import serializers
from shipping.models import ShippingZone, ShippingRate, Shipment


class ShippingZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingZone
        fields = ('id', 'name', 'countries', 'is_active')


class ShippingRateSerializer(serializers.ModelSerializer):
    zone_name = serializers.CharField(source='zone.name', read_only=True)
    class Meta:
        model = ShippingRate
        fields = ('id', 'zone_name', 'method', 'price', 'estimated_days_min', 'estimated_days_max')


class ShipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipment
        fields = ('id', 'order_id', 'tracking_number', 'carrier', 'status',
                  'shipped_at', 'estimated_delivery', 'delivered_at', 'created_at')
