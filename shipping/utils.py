"""
shipping/utils.py - Shipping business logic
Depends on: shipping.models, orders.models, accounts.models
"""
from django.utils import timezone
from shipping.models import Shipment, ShippingZone, ShippingRate
from accounts.models import Address
from orders.models import Order
from notifications.utils import send_order_notification


def create_shipment_for_order(order):
    """Create a Shipment record when an order is confirmed."""
    if hasattr(order, 'shipment'):
        return order.shipment  # Already has a shipment

    shipment = Shipment.objects.create(
        order_id=order.pk,
        shipping_address=order.shipping_address,
        shipping_rate=order.shipping_rate,
        status='processing',
    )
    return shipment


def get_shipping_rates_for_address(address):
    """Get applicable shipping rates for a given address."""
    country = address.country if isinstance(address, Address) else address
    zones = ShippingZone.objects.filter(is_active=True)
    matching_zones = []
    for zone in zones:
        if country in zone.get_countries_list():
            matching_zones.append(zone.pk)

    rates = ShippingRate.objects.filter(
        zone_id__in=matching_zones, is_active=True
    ).order_by('price')
    return rates


def update_shipment_tracking(shipment_id, tracking_number, carrier, status='shipped'):
    """Update tracking info for a shipment."""
    shipment = Shipment.objects.get(pk=shipment_id)
    updates = {
        'tracking_number': tracking_number,
        'carrier': carrier,
        'status': status,
    }
    if status == 'shipped':
        updates['shipped_at'] = timezone.now()
    elif status == 'delivered':
        updates['delivered_at'] = timezone.now()

    Shipment.objects.filter(pk=shipment_id).update(**updates)

    # Notify user about shipment
    try:
        order = Order.objects.get(pk=shipment.order_id)
        send_order_notification(order, 'order_shipped')
        Order.objects.filter(pk=order.pk).update(status='shipped')
    except Order.DoesNotExist:
        pass

    return Shipment.objects.get(pk=shipment_id)