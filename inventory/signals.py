"""
inventory/signals.py - Signal handlers for inventory
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from inventory.models import StockLevel


@receiver(post_save, sender=StockLevel)
def check_low_stock_on_update(sender, instance, **kwargs):
    """Send a low stock alert if stock drops below the reorder threshold."""
    if instance.is_low_stock():
        from notifications.utils import send_admin_notification
        send_admin_notification(
            'low_stock_alert',
            'Low Stock: %s' % instance.product.name,
            'Only %d units remaining for %s. Reorder threshold: %d.' % (
                instance.available_quantity, instance.product.name, instance.reorder_threshold
            )
        )
