"""Orders helper file."""

from django.db.models import Q

def process_installment(installment):
    """Process installement."""
    installment_item = installment.installment_item
    installment_item.amount_paid += installment.amount
    no_of_cleared_items = int(
        float(installment_item.amount_paid) / installment_item.unit_price) if installment_item.unit_price else 0    # noqa
    installment_item.no_of_items_cleared = no_of_cleared_items
    installment_item.save()

    return installment_item

def refresh_order(order):
    from elites_franchise_portal.orders.models import (
        Cart, CartItem, InstallmentsOrderItem, InstantOrderItem)
    customer = order.customer
    InstantOrderItem.objects.filter(order=order)
    InstallmentsOrderItem.objects.filter(order=order)
    carts = Cart.objects.filter(
        Q(order_guid=order.id) | Q(cart_code=order.cart_code),
        franchise=order.franchise)

    if not customer.is_franchise:
        carts.update(customer=customer)
    import pdb
    pdb.set_trace()
    # Get all sales attached to this order
    # Get all the order items
    # Get all Order Transactions
    # Now Process This
