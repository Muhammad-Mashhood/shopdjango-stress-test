"""
analytics/utils.py - Analytics data collection and reporting
Depends on: analytics.models, orders.models, products.models, payments.models
"""
from django.utils import timezone
from datetime import timedelta

from analytics.models import ProductView, SearchQuery, SalesReport, ProductPerformance
from orders.models import Order, OrderItem
from products.models import Product
from payments.models import Payment


def record_product_view(product, user=None, session_key=None, ip_address=None, referrer=''):
    """Record a product page view in analytics."""
    ProductView.objects.create(
        product=product,
        user=user,
        session_key=session_key or '',
        ip_address=ip_address,
        referrer=referrer,
    )


def record_search(query, user=None, results_count=0, clicked_product_id=None):
    """Record a search query."""
    clicked_product = None
    if clicked_product_id:
        try:
            clicked_product = Product.objects.get(pk=clicked_product_id)
        except Product.DoesNotExist:
            pass

    SearchQuery.objects.create(
        user=user,
        query=query,
        results_count=results_count,
        clicked_product=clicked_product,
    )


def get_top_selling_products(limit=10, days=30):
    """Return the top-selling products in the last N days."""
    since = timezone.now() - timedelta(days=days)
    from django.db.models import Sum
    top = OrderItem.objects.filter(
        order__created_at__gte=since,
        order__status__in=['delivered', 'shipped']
    ).values('product_id').annotate(
        total_sold=Sum('quantity')
    ).order_by('-total_sold')[:limit]

    product_ids = [item['product_id'] for item in top]
    products = Product.objects.filter(pk__in=product_ids)
    return products


def get_revenue_by_period(period='week'):
    """Calculate total revenue for a given period."""
    from django.db.models import Sum
    now = timezone.now()
    if period == 'week':
        since = now - timedelta(days=7)
    elif period == 'month':
        since = now - timedelta(days=30)
    else:
        since = now - timedelta(days=365)

    result = Payment.objects.filter(
        created_at__gte=since, status='completed'
    ).aggregate(total=Sum('amount'))
    return result['total'] or 0


def generate_daily_report(date):
    """Generate or update a daily sales report."""
    from django.db.models import Sum, Count
    start = timezone.datetime.combine(date, timezone.datetime.min.time())
    end = timezone.datetime.combine(date, timezone.datetime.max.time())

    if timezone.is_naive(start):
        import pytz
        start = timezone.make_aware(start)
        end = timezone.make_aware(end)

    orders = Order.objects.filter(created_at__range=(start, end))
    totals = orders.aggregate(
        order_count=Count('id'),
        revenue=Sum('total'),
        items=Sum('items__quantity'),
    )

    new_customers = Order.objects.filter(
        created_at__range=(start, end)
    ).values('user_id').distinct().count()

    report, _ = SalesReport.objects.update_or_create(
        date=date,
        defaults={
            'total_orders': totals['order_count'] or 0,
            'total_revenue': totals['revenue'] or 0,
            'total_items_sold': totals['items'] or 0,
            'new_customers': new_customers,
            'average_order_value': (
                (totals['revenue'] or 0) / (totals['order_count'] or 1)
            ),
        }
    )
    return report
