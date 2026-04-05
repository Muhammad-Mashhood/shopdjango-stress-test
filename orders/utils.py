"""
orders/utils.py - Business logic for order management
Depends on: orders.models, accounts.models, products.models, discounts.models, shipping.models
"""
import uuid
from django.utils import timezone
from django.utils.encoding import force_str

from orders.models import Cart, CartItem, Order
from accounts.models import Address
from discounts.models import Discount, DiscountUsage
from shipping.models import ShippingRate


def generate_order_number():
    """Generate a unique order number."""
    return 'ORD-%s' % str(uuid.uuid4()).replace('-', '')[:12].upper()


def calculate_cart_totals(cart, discount=None, shipping_rate=None):
    """Calculate subtotal, discount, shipping, tax, and total for a cart."""
    subtotal = cart.get_total()
    discount_amount = 0
    shipping_cost = 0
    tax_rate = 0.08  # 8% tax

    if discount and discount.is_valid:
        discount_amount = float(discount.calculate_discount(subtotal))

    if shipping_rate:
        shipping_cost = float(shipping_rate.price)

    taxable_amount = float(subtotal) - discount_amount + shipping_cost
    tax_amount = round(taxable_amount * tax_rate, 2)
    total = taxable_amount + tax_amount

    return {
        'subtotal': float(subtotal),
        'discount_amount': discount_amount,
        'shipping_cost': shipping_cost,
        'tax_amount': tax_amount,
        'total': total,
    }


def apply_discount_to_cart(cart, discount_code, user):
    """Validate and return a discount for the cart."""
    try:
        discount = Discount.objects.get(code=discount_code, is_active=True)
    except Discount.DoesNotExist:
        return None, force_str('Invalid discount code')

    if not discount.is_valid:
        return None, force_str('Discount is expired or no longer available')

    # Check per-user usage
    user_usage = DiscountUsage.objects.filter(discount=discount, user=user).count()
    if user_usage >= discount.per_user_limit:
        return None, force_str('You have already used this discount')

    return discount, None


def create_order_from_cart(cart, user, discount_code=None, shipping_rate_id=None,
                           billing_address_id=None, shipping_address_id=None):
    """Create an Order from a Cart."""
    discount = None
    if discount_code:
        discount, error = apply_discount_to_cart(cart, discount_code, user)

    shipping_rate = None
    if shipping_rate_id:
        try:
            shipping_rate = ShippingRate.objects.get(pk=shipping_rate_id, is_active=True)
        except ShippingRate.DoesNotExist:
            pass

    billing_address = None
    if billing_address_id:
        try:
            billing_address = Address.objects.get(pk=billing_address_id, user=user)
        except Address.DoesNotExist:
            pass

    shipping_address = None
    if shipping_address_id:
        try:
            shipping_address = Address.objects.get(pk=shipping_address_id, user=user)
        except Address.DoesNotExist:
            pass

    totals = calculate_cart_totals(cart, discount, shipping_rate)

    order = Order.objects.create(
        user=user,
        order_number=generate_order_number(),
        billing_address=billing_address,
        shipping_address=shipping_address,
        shipping_rate=shipping_rate,
        discount=discount,
        subtotal=totals['subtotal'],
        discount_amount=totals['discount_amount'],
        shipping_cost=totals['shipping_cost'],
        tax_amount=totals['tax_amount'],
        total=totals['total'],
        payment_method='stripe',
    )

    # Create order items from cart items
    for cart_item in cart.items.select_related('product', 'variant'):
        unit_price = cart_item.variant.get_price() if cart_item.variant else cart_item.product.price
        OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            variant=cart_item.variant,
            product_name=cart_item.product.name,
            product_sku=cart_item.product.sku,
            quantity=cart_item.quantity,
            unit_price=unit_price,
            total_price=unit_price * cart_item.quantity,
        )

    # Record discount usage
    if discount:
        DiscountUsage.objects.create(discount=discount, user=user, order_id=order.pk)
        Discount.objects.filter(pk=discount.pk).update(used_count=discount.used_count + 1)

    # Clear the cart
    cart.items.all().delete()

    return order