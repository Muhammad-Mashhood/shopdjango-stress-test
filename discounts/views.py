"""
discounts/views.py - Discount management views
Depends on: discounts.models, discounts.serializers, orders.models
"""
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_text

from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from discounts.models import Discount
from discounts.serializers import DiscountSerializer


class DiscountListView(generics.ListCreateAPIView):
    queryset = Discount.objects.filter(is_active=True)
    serializer_class = DiscountSerializer
    permission_classes = (permissions.IsAdminUser,)


class DiscountDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer
    permission_classes = (permissions.IsAdminUser,)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def validate_discount(request):
    """Validate a discount code for the current cart."""
    code = request.data.get('code', '').upper()
    try:
        discount = Discount.objects.get(code=code, is_active=True)
        if discount.is_valid():
            return Response({
                'valid': True,
                'discount_type': discount.discount_type,
                'value': float(discount.value),
            })
        return Response({'valid': False, 'message': force_text(_('Discount is expired or exhausted'))})
    except Discount.DoesNotExist:
        return Response({'valid': False, 'message': force_text(_('Invalid discount code'))})
