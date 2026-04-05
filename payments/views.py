"""
payments/views.py - Payment processing views
Depends on: payments.models, payments.utils, orders.models, notifications.utils
"""
import stripe
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import gettext_lazy as _
from django.utils.encoding import force_str

from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from payments.models import Payment, Refund, SavedPaymentMethod
from payments.serializers import PaymentSerializer, RefundSerializer
from payments.utils import process_stripe_payment, process_refund
from orders.models import Order
from notifications.utils import send_payment_notification

stripe.api_key = settings.STRIPE_SECRET_KEY


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_payment_intent(request):
    """Create a Stripe PaymentIntent for an order."""
    order_id = request.data.get('order_id')
    try:
        order = Order.objects.get(pk=order_id, user=request.user, payment_status='pending')
    except Order.DoesNotExist:
        return Response({'error': force_str(_('Order not found'))}, status=status.HTTP_404_NOT_FOUND)

    try:
        intent = stripe.PaymentIntent.create(
            amount=int(order.total * 100),  # Amount in cents
            currency='usd',
            metadata={'order_id': order.pk, 'order_number': order.order_number}
        )
        return Response({'client_secret': intent['client_secret']})
    except stripe.error.StripeError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def confirm_payment(request):
    """Confirm a successful payment from the frontend."""
    order_id = request.data.get('order_id')
    payment_intent_id = request.data.get('payment_intent_id')

    try:
        order = Order.objects.get(pk=order_id, user=request.user)
        payment = process_stripe_payment(order, payment_intent_id, request.user)
        send_payment_notification(payment, success=True)
        return Response(PaymentSerializer(payment).data)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def process_refund_view(request):
    """Process a refund for a payment."""
    payment_id = request.data.get('payment_id')
    amount = request.data.get('amount')
    reason = request.data.get('reason', '')

    try:
        payment = Payment.objects.get(pk=payment_id)
        refund = process_refund(payment, amount, reason, request.user)
        send_payment_notification(payment, success=False)
        return Response(RefundSerializer(refund).data)
    except Payment.DoesNotExist:
        return Response({'error': force_str(_('Payment not found'))}, status=status.HTTP_404_NOT_FOUND)


class PaymentHistoryView(generics.ListAPIView):
    """List payment history for the authenticated user."""
    serializer_class = PaymentSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user).order_by('-created_at')
