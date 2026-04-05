"""
orders/views.py - Order management views
Depends on: orders.models, orders.serializers, orders.utils, payments.utils, notifications.utils
"""
from django.core.urlresolvers import reverse
from django.utils.translation import gettext_lazy as _
from django.utils.encoding import force_str

from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from orders.models import Cart, CartItem, Order, OrderItem
from orders.serializers import CartSerializer, OrderSerializer, OrderListSerializer
from orders.utils import (
    create_order_from_cart, generate_order_number,
    apply_discount_to_cart, calculate_cart_totals
)
from inventory.utils import reserve_stock, release_stock
from notifications.utils import send_order_notification


class CartView(generics.RetrieveAPIView):
    """Get the current user's cart."""
    serializer_class = CartSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_to_cart(request):
    """Add a product to the cart."""
    cart, _ = Cart.objects.get_or_create(user=request.user)
    product_id = request.data.get('product_id')
    variant_id = request.data.get('variant_id')
    quantity = int(request.data.get('quantity', 1))

    from products.models import Product, ProductVariant
    try:
        product = Product.objects.get(pk=product_id, status='active')
    except Product.DoesNotExist:
        return Response({'error': force_str(_('Product not found'))}, status=status.HTTP_404_NOT_FOUND)

    variant = None
    if variant_id:
        try:
            variant = ProductVariant.objects.get(pk=variant_id, product=product)
        except ProductVariant.DoesNotExist:
            return Response({'error': force_str(_('Variant not found'))}, status=status.HTTP_404_NOT_FOUND)

    item, created = CartItem.objects.get_or_create(
        cart=cart, product=product, variant=variant,
        defaults={'quantity': quantity}
    )
    if not created:
        item.quantity += quantity
        item.save()

    return Response({'message': force_str(_('Added to cart')), 'item_count': cart.get_item_count()})


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def remove_from_cart(request, item_id):
    """Remove an item from the cart."""
    try:
        cart = Cart.objects.get(user=request.user)
        item = CartItem.objects.get(pk=item_id, cart=cart)
        item.delete()
        return Response({'message': force_str(_('Item removed'))})
    except (Cart.DoesNotExist, CartItem.DoesNotExist):
        return Response({'error': force_str(_('Item not found'))}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def checkout(request):
    """Convert cart to order."""
    try:
        cart = Cart.objects.get(user=request.user)
        if not cart.items.exists():
            return Response({'error': force_str(_('Cart is empty'))}, status=status.HTTP_400_BAD_REQUEST)

        discount_code = request.data.get('discount_code')
        shipping_rate_id = request.data.get('shipping_rate_id')
        billing_address_id = request.data.get('billing_address_id')
        shipping_address_id = request.data.get('shipping_address_id')

        order = create_order_from_cart(
            cart=cart,
            user=request.user,
            discount_code=discount_code,
            shipping_rate_id=shipping_rate_id,
            billing_address_id=billing_address_id,
            shipping_address_id=shipping_address_id,
        )
        reserve_stock(order)
        send_order_notification(order, 'order_placed')
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Cart.DoesNotExist:
        return Response({'error': force_str(_('Cart not found'))}, status=status.HTTP_404_NOT_FOUND)


class OrderListView(generics.ListAPIView):
    """List all orders for the authenticated user."""
    serializer_class = OrderListSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')


class OrderDetailView(generics.RetrieveAPIView):
    """Get a specific order for the authenticated user."""
    serializer_class = OrderSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
