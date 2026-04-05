"""
inventory/serializers.py - DRF serializers for inventory
"""
from rest_framework import serializers
from inventory.models import StockLevel, StockMovement, Warehouse


class StockLevelSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    available_quantity = serializers.ReadOnlyField()

    class Meta:
        model = StockLevel
        fields = ('id', 'product_name', 'product_sku', 'quantity',
                  'reserved_quantity', 'available_quantity', 'reorder_threshold', 'updated_at')


class StockMovementSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = StockMovement
        fields = ('id', 'product_name', 'movement_type', 'quantity', 'reference', 'notes', 'created_at')


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = ('id', 'name', 'code', 'address', 'is_active')
