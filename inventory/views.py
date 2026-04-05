"""
inventory/views.py - Inventory management views
Depends on: inventory.models, inventory.serializers, inventory.utils
"""
from django.utils.translation import gettext_lazy as _
from django.utils.encoding import force_str

from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from inventory.models import StockLevel, StockMovement
from inventory.serializers import StockLevelSerializer, StockMovementSerializer
from inventory.utils import add_stock


class StockListView(generics.ListAPIView):
    queryset = StockLevel.objects.select_related('product').all()
    serializer_class = StockLevelSerializer
    permission_classes = (permissions.IsAdminUser,)


class StockDetailView(generics.RetrieveUpdateAPIView):
    queryset = StockLevel.objects.all()
    serializer_class = StockLevelSerializer
    permission_classes = (permissions.IsAdminUser,)


class StockMovementListView(generics.ListAPIView):
    queryset = StockMovement.objects.select_related('product').order_by('-created_at')
    serializer_class = StockMovementSerializer
    permission_classes = (permissions.IsAdminUser,)


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def add_stock_view(request):
    """Manually add stock for a product."""
    from products.models import Product
    product_id = request.data.get('product_id')
    quantity = int(request.data.get('quantity', 0))
    notes = request.data.get('notes', '')

    try:
        product = Product.objects.get(pk=product_id)
        add_stock(product, quantity, notes=notes)
        return Response({'message': force_str(_('Stock updated successfully'))})
    except Product.DoesNotExist:
        return Response({'error': force_str(_('Product not found'))}, status=status.HTTP_404_NOT_FOUND)
