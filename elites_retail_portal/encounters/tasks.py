"""Encounters tasks file."""

import random
from decimal import Decimal

from elites_retail_portal.catalog.models import (
    CatalogItem)
from elites_retail_portal.encounters.models import Encounter
from elites_retail_portal.orders.models import (
    CartItem, Cart, Order, OrderTransaction)
from elites_retail_portal.orders.helpers.orders import process_order_transaction

from elites_retail_portal.transactions.models import Payment, Transaction

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
        order = Order.objects.get(id=cart.order_guid, enterprise=encounter.enterprise)

        encounter.order_guid = order.id
        encounter.processing_status = 'BILLING DONE'
        encounter.save()
        order.process_order()
        encounter.refresh_from_db()
        payments = encounter.payments
        transaction_code = f"{random.randint(10000, 999999)}"
        encounter_payments = []

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
                    'transaction_code': transaction_code
                }
                payment = Payment.objects.create(**payment_payload, **audit_fields)
                encounter_payments.append(payment)
                encounter.payments[count]['payment_guid'] = str(payment.id)

        for payment in encounter_payments:
            transaction_filter = {
                'transaction_code': transaction_code,
                'enterprise': encounter.enterprise,
            }
            transaction = Transaction.objects.filter(**transaction_filter).first()

            if transaction:
                transaction.amount += payment.paid_amount
                transaction.balance += payment.paid_amount
                transaction.save()
                payment.transaction_guid = transaction.id
                payment.save()

            else:
                transaction_payload = {
                    'account_number': payment.account_number,
                    'amount': payment.paid_amount,
                    'transaction_means': payment.payment_method,
                    'customer': encounter.customer,
                    'transaction_code': payment.transaction_code,
                }
                transaction = Transaction.objects.create(**transaction_payload, **audit_fields)
                payment.transaction_guid = transaction.id
                payment.save()

        # Update transaction amounts using the encounter balance
        transaction.refresh_from_db()
        transaction.amount -= Decimal(encounter.balance_amount)
        transaction.balance -= Decimal(encounter.balance_amount)
        transaction.save()

        order = Order.objects.get(id=encounter.order_guid)
        order_transaction_payload = {
            'amount': transaction.balance,
            'order': order,
            'transaction': transaction,
        }
        order_transaction = OrderTransaction.objects.create(**order_transaction_payload, **audit_fields)
        order_transaction.refresh_from_db()
        process_order_transaction(order_transaction)
        encounter.processing_status = 'SUCCESS'
        encounter.save()

    return encounter
