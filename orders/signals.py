"""
orders/signals.py - Signal handlers for orders
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from orders.models import Order


@receiver(post_save, sender=Order)
def order_status_changed(sender, instance, created, **kwargs):
    """When order status changes, trigger analytics update."""
    if not created and instance.status == 'delivered':
        from analytics.utils import record_product_view
        for item in instance.items.all():
            from analytics.models import ProductPerformance
            from django.utils import timezone
            import datetime
            week_start = timezone.now().date() - datetime.timedelta(days=timezone.now().weekday())
            perf, _ = ProductPerformance.objects.get_or_create(
                product=item.product,
                week_start=week_start,
                defaults={}
            )
            ProductPerformance.objects.filter(pk=perf.pk).update(
                purchase_count=perf.purchase_count + item.quantity,
                revenue=float(perf.revenue) + float(item.total_price)
            )
