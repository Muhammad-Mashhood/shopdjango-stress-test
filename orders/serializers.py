"""
orders/serializers.py - DRF serializers for orders
Depends on: orders.models, products.serializers, accounts.serializers, shipping.serializers
"""
from rest_framework import serializers
from orders.models import Cart, CartItem, Order, OrderItem
from products.serializers import ProductListSerializer
from accounts.serializers import AddressSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ('id', 'product', 'variant', 'quantity', 'subtotal', 'added_at')

    def get_subtotal(self, obj):
        return float(obj.get_subtotal())


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ('id', 'items', 'total', 'item_count', 'updated_at')

    def get_total(self, obj):
        return float(obj.get_total())

    def get_item_count(self, obj):
        return obj.get_item_count()


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = (
            'id', 'product', 'product_name', 'product_sku',
            'quantity', 'unit_price', 'discount_amount', 'total_price'
        )


class OrderListSerializer(serializers.ModelSerializer):
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            'id', 'order_number', 'status', 'total',
            'payment_status', 'created_at', 'item_count'
        )

    def get_item_count(self, obj):
        return obj.items.count()


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    billing_address = AddressSerializer(read_only=True)
    shipping_address = AddressSerializer(read_only=True)

    class Meta:
        model = Order
        fields = (
            'id', 'order_number', 'status', 'items',
            'billing_address', 'shipping_address',
            'subtotal', 'discount_amount', 'shipping_cost', 'tax_amount', 'total',
            'payment_method', 'payment_status', 'notes', 'created_at'
        )
