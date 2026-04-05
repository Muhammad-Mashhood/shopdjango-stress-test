from django.contrib import admin
from payments.models import Payment, Refund, SavedPaymentMethod


class RefundInline(admin.TabularInline):
    model = Refund
    extra = 0
    readonly_fields = ('amount', 'reason', 'gateway_refund_id', 'created_at')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'user', 'gateway', 'amount', 'status', 'created_at')
    list_filter = ('gateway', 'status', 'created_at')
    search_fields = ('order__order_number', 'user__email', 'gateway_transaction_id')
    readonly_fields = ('gateway_transaction_id', 'gateway_response', 'created_at')
    inlines = [RefundInline]
    raw_id_fields = ('order', 'user')


@admin.register(SavedPaymentMethod)
class SavedPaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('user', 'brand', 'last4', 'exp_month', 'exp_year', 'is_default')
    raw_id_fields = ('user',)
