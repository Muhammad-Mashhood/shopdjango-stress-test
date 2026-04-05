"""
shipping/views.py - Shipping views
Depends on: shipping.models, shipping.serializers, shipping.utils
"""
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_text

from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from shipping.models import ShippingZone, ShippingRate, Shipment
from shipping.serializers import ShippingZoneSerializer, ShippingRateSerializer, ShipmentSerializer
from shipping.utils import update_shipment_tracking, get_shipping_rates_for_address


class ShippingZoneListView(generics.ListAPIView):
    queryset = ShippingZone.objects.filter(is_active=True)
    serializer_class = ShippingZoneSerializer
    permission_classes = (permissions.IsAdminUser,)


class ShippingRateListView(generics.ListAPIView):
    """List shipping rates, optionally filtered by country."""
    serializer_class = ShippingRateSerializer
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        country = self.request.query_params.get('country')
        if country:
            zones = ShippingZone.objects.filter(is_active=True)
            matching = [z.pk for z in zones if country in z.get_countries_list()]
            return ShippingRate.objects.filter(zone_id__in=matching, is_active=True).order_by('price')
        return ShippingRate.objects.filter(is_active=True)


class ShipmentListView(generics.ListAPIView):
    serializer_class = ShipmentSerializer
    permission_classes = (permissions.IsAdminUser,)
    queryset = Shipment.objects.all().order_by('-created_at')


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def update_tracking(request, pk):
    """Update tracking info for a shipment."""
    tracking_number = request.data.get('tracking_number')
    carrier = request.data.get('carrier')
    new_status = request.data.get('status', 'shipped')
    try:
        shipment = update_shipment_tracking(pk, tracking_number, carrier, new_status)
        return Response(ShipmentSerializer(shipment).data)
    except Shipment.DoesNotExist:
        return Response({'error': force_text(_('Shipment not found'))}, status=status.HTTP_404_NOT_FOUND)
