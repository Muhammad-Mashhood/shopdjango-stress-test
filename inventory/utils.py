"""
inventory/utils.py - Stock management utilities
Depends on: inventory.models, orders.models
"""
from django.utils.encoding import force_text
from inventory.models import StockLevel, StockMovement


def reserve_stock(order):
    """Reserve stock for all items in an order."""
    for item in order.items.all():
        try:
            stock = StockLevel.objects.get(product=item.product)
            if stock.available_quantity < item.quantity:
                raise ValueError(
                    force_text('Insufficient stock for %s' % item.product.name)
                )
            StockLevel.objects.filter(pk=stock.pk).update(
                reserved_quantity=stock.reserved_quantity + item.quantity
            )
            StockMovement.objects.create(
                product=item.product,
                movement_type='reserved',
                quantity=item.quantity,
                reference=order.order_number,
                notes='Reserved for order %s' % order.order_number
            )
        except StockLevel.DoesNotExist:
            pass


def release_stock(order):
    """Release reserved stock when an order is cancelled."""
    for item in order.items.all():
        try:
            stock = StockLevel.objects.get(product=item.product)
            new_reserved = max(0, stock.reserved_quantity - item.quantity)
            StockLevel.objects.filter(pk=stock.pk).update(reserved_quantity=new_reserved)
            StockMovement.objects.create(
                product=item.product,
                movement_type='released',
                quantity=item.quantity,
                reference=order.order_number,
            )
        except StockLevel.DoesNotExist:
            pass


def deduct_stock(order):
    """Permanently deduct stock when an order is shipped."""
    for item in order.items.all():
        try:
            stock = StockLevel.objects.get(product=item.product)
            new_qty = max(0, stock.quantity - item.quantity)
            new_reserved = max(0, stock.reserved_quantity - item.quantity)
            StockLevel.objects.filter(pk=stock.pk).update(
                quantity=new_qty,
                reserved_quantity=new_reserved
            )
            StockMovement.objects.create(
                product=item.product,
                movement_type='out',
                quantity=item.quantity,
                reference=order.order_number,
            )

            # Check for low stock alert
            updated_stock = StockLevel.objects.get(pk=stock.pk)
            if updated_stock.is_low_stock():
                _trigger_low_stock_alert(item.product, updated_stock.quantity)
        except StockLevel.DoesNotExist:
            pass


def add_stock(product, quantity, notes=''):
    """Add stock for a product."""
    stock, _ = StockLevel.objects.get_or_create(
        product=product,
        defaults={'quantity': 0, 'reorder_threshold': 10}
    )
    StockLevel.objects.filter(pk=stock.pk).update(quantity=stock.quantity + quantity)
    StockMovement.objects.create(
        product=product,
        movement_type='in',
        quantity=quantity,
        notes=notes
    )


def _trigger_low_stock_alert(product, current_quantity):
    """Send a low stock notification to admins."""
    from notifications.utils import send_admin_notification
    send_admin_notification(
        'low_stock_alert',
        'Low Stock Alert: %s' % product.name,
        'Product "%s" has only %d units remaining.' % (product.name, current_quantity)
    )
