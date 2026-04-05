from rest_framework import serializers
from discounts.models import Discount, DiscountUsage


class DiscountSerializer(serializers.ModelSerializer):
    is_valid_now = serializers.SerializerMethodField()

    class Meta:
        model = Discount
        fields = ('id', 'name', 'code', 'discount_type', 'value', 'min_purchase_amount',
                  'max_discount_amount', 'usage_limit', 'used_count', 'valid_from',
                  'valid_until', 'is_active', 'is_valid_now')

    def get_is_valid_now(self, obj):
        return obj.is_valid()
