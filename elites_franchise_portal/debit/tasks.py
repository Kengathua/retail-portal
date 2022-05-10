"""Debit side tasks file."""

from elites_franchise_portal.orders.models import (
    Cart, Order,)


def process_sale(sale):
    """Process sale record."""
    cart = Cart.objects.get(
        customer=sale.customer, sale=sale, is_active=True, is_checked_out=False)
    cart.checkout_cart()
    order = Order.objects.get(customer=sale.customer, cart_code=cart.cart_code)
    order.process_order()
