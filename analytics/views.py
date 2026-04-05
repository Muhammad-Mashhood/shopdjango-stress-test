"""
analytics/views.py - Analytics dashboard views
Depends on: analytics.models, analytics.utils, orders.models, products.models
"""
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from analytics.models import ProductView, SearchQuery, SalesReport, ProductPerformance
from analytics.serializers import SalesReportSerializer, ProductPerformanceSerializer
from analytics.utils import (
    record_product_view, record_search, generate_daily_report,
    get_top_selling_products, get_revenue_by_period
)
from orders.models import Order
from products.models import Product


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def track_product_view(request, product_id):
    """Record a product page view."""
    try:
        product = Product.objects.get(pk=product_id)
        record_product_view(
            product=product,
            user=request.user if request.user.is_authenticated() else None,
            session_key=request.session.session_key,
            ip_address=request.META.get('REMOTE_ADDR'),
            referrer=request.META.get('HTTP_REFERER', ''),
        )
        return Response({'recorded': True})
    except Product.DoesNotExist:
        return Response({'recorded': False})


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def track_search(request):
    """Record a user search query."""
    query = request.data.get('query', '')
    results_count = request.data.get('results_count', 0)
    clicked_product_id = request.data.get('clicked_product_id')

    if query:
        record_search(
            query=query,
            user=request.user if request.user.is_authenticated() else None,
            results_count=results_count,
            clicked_product_id=clicked_product_id,
        )
    return Response({'recorded': True})


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def dashboard_summary(request):
    """Return a high-level analytics summary for the admin dashboard."""
    from django.utils import timezone
    from datetime import timedelta

    today = timezone.now().date()
    week_ago = today - timedelta(days=7)

    total_orders = Order.objects.count()
    recent_orders = Order.objects.filter(created_at__date__gte=week_ago).count()
    total_products = Product.objects.filter(status='active').count()

    top_products = get_top_selling_products(limit=5)
    revenue = get_revenue_by_period('week')

    return Response({
        'total_orders': total_orders,
        'recent_orders': recent_orders,
        'total_products': total_products,
        'top_products': [{'name': p.name, 'id': p.pk} for p in top_products],
        'weekly_revenue': float(revenue),
    })


class SalesReportListView(generics.ListAPIView):
    """List daily sales reports."""
    serializer_class = SalesReportSerializer
    permission_classes = (permissions.IsAdminUser,)
    queryset = SalesReport.objects.all().order_by('-date')[:30]


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def generate_report(request):
    """Manually trigger a daily report generation."""
    from django.utils import timezone
    date = timezone.now().date()
    report = generate_daily_report(date)
    return Response(SalesReportSerializer(report).data)
