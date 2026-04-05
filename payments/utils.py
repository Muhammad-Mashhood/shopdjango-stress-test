"""
payments/utils.py - Payment processing helper functions
Depends on: payments.models, orders.models, shipping.utils
"""
import stripe
from django.conf import settings
from django.utils import timezone

from payments.models import Payment, Refund
from orders.models import Order

stripe.api_key = settings.STRIPE_SECRET_KEY


def process_stripe_payment(order, payment_intent_id, user):
    """Record a successful Stripe payment."""
    # Verify intent with Stripe
    try:
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        gateway_response = str(intent)
    except stripe.error.StripeError:
        gateway_response = ''

    payment = Payment.objects.create(
        order=order,
        user=user,
        gateway='stripe',
        gateway_transaction_id=payment_intent_id,
        gateway_response=gateway_response,
        amount=order.total,
        status='completed',
    )
    Order.objects.filter(pk=order.pk).update(payment_status='paid', status='confirmed')

    # Trigger shipping notification
    from shipping.utils import create_shipment_for_order
    create_shipment_for_order(order)

    return payment


def process_refund(payment, amount, reason, processed_by):
    """Process a refund via Stripe and record it."""
    try:
        stripe.Refund.create(
            payment_intent=payment.gateway_transaction_id,
            amount=int(float(amount) * 100),
        )
        refund_status = 'refunded'
    except stripe.error.StripeError:
        refund_status = payment.status

    refund = Refund.objects.create(
        payment=payment,
        amount=amount,
        reason=reason,
        processed_by=processed_by,
    )
    Payment.objects.filter(pk=payment.pk).update(status='refunded')
    Order.objects.filter(pk=payment.order_id).update(status='refunded')
    return refund
