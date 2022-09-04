"""Encounters tasks file."""

from elites_franchise_portal.encounters.models import Encounter
from elites_franchise_portal.catalog.models import (
    CatalogItem)
from elites_franchise_portal.orders.models import (
    CartItem, Cart, Order)
from elites_franchise_portal.transactions.models import Payment

from celery import shared_task

@shared_task(name=__name__ + '.process_customer_encounter', ignore_result=True)
def process_customer_encounter(encounter_id):
    """Process customer encounter."""
    encounters = Encounter.objects.filter(id=encounter_id)
    encounters.update(processing_status='ONGOING')
    encounter = encounters.first()
    audit_fields = {
        'created_by': encounter.created_by,
        'updated_by': encounter.updated_by,
        'franchise': encounter.franchise,
    }

    cart = Cart.objects.filter(encounter=encounter).first()
    if not cart:
        cart = Cart.objects.create(
            encounter=encounter, customer=encounter.customer, **audit_fields)

    for bill in encounter.billing:
        catalog_item = CatalogItem.objects.get(id=bill['catalog_item'])
        sale_type = bill['sale_type']
        payload = {
            'cart': cart,
            'catalog_item': catalog_item,
            'quantity_added': bill['quantity'],
            'selling_price': bill['unit_price'],
            'is_installment': True if sale_type == 'INSTALLMENT' else False
        }

        CartItem.objects.create(**payload, **audit_fields)

    cart.checkout_cart()
    order = Order.objects.get(
        customer=cart.customer, cart_code=cart.cart_code,
        franchise=encounter.franchise)
    order.process_order()

    payments = encounter.payments
    for payment in payments:
        means = payment['means']
        amount = payment['amount']
        if amount:
            payment_payload = {
                'paid_amount': amount,
                'customer': encounter.customer,
                'payment_method': means,
                'is_confirmed': True,
                'required_amount': amount,
            }
            Payment.objects.create(**payment_payload, **audit_fields)

    encounters.update(processing_status='SUCCESS')
    encounter.refresh_from_db()
    return encounter
