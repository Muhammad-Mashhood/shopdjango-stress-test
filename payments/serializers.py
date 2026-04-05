"""
payments/serializers.py - DRF serializers for payments
"""
from rest_framework import serializers
from payments.models import Payment, Refund, SavedPaymentMethod


class RefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refund
        fields = ('id', 'amount', 'reason', 'gateway_refund_id', 'created_at')


class PaymentSerializer(serializers.ModelSerializer):
    refunds = RefundSerializer(many=True, read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)

    class Meta:
        model = Payment
        fields = ('id', 'order_number', 'gateway', 'amount', 'currency',
                  'status', 'refunds', 'created_at')


class SavedPaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedPaymentMethod
        fields = ('id', 'gateway', 'last4', 'brand', 'exp_month', 'exp_year', 'is_default')
