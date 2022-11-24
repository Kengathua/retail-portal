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
    if encounter:
        audit_fields = {
            'created_by': encounter.created_by,
            'updated_by': encounter.updated_by,
            'enterprise': encounter.enterprise,
        }

        cart = Cart.objects.filter(encounter=encounter).first()
        if not cart:
            cart = Cart.objects.create(
                encounter=encounter, customer=encounter.customer, **audit_fields)

        encounters.update(cart_guid=cart.id)

        for bill in encounter.billing:
            catalog_item = CatalogItem.objects.get(id=bill['catalog_item'])
            sale_type = bill['sale_type']
            cart_item_payload = {
                'cart': cart,
                'catalog_item': catalog_item,
                'quantity_added': bill['quantity'],
                'selling_price': bill['unit_price'],
                'is_installment': True if sale_type == 'INSTALLMENT' else False
            }

            CartItem.objects.create(**cart_item_payload, **audit_fields)

        cart.checkout_cart()
        encounter.refresh_from_db()
        if not encounter.cart_guid:
            import pdb
            pdb.set_trace()
        order = Order.objects.get(id=cart.order_guid, enterprise=encounter.enterprise)

        encounter.order_guid = order.id
        encounter.processing_status = 'BILLING DONE'
        encounter.save()
        order.process_order()
        encounter.refresh_from_db()
        payments = encounter.payments
        for count, payment in enumerate(payments):
            means = payment['means']
            amount = payment['amount']
            if amount:
                account_number = encounter.customer.account_number or encounter.customer.customer_number or encounter.customer.phone_no
                payment_payload = {
                    'paid_amount': amount,
                    'customer': encounter.customer,
                    'payment_method': means,
                    'is_confirmed': True,
                    'required_amount': amount,
                    'encounter': encounter,
                    'account_number':account_number,
                }
                payment = Payment.objects.create(**payment_payload, **audit_fields)
                encounter.payments[count]['payment_guid'] = str(payment.id)

        encounter.processing_status = 'SUCCESS'
        encounter.save()
    return encounter
