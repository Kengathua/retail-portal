"""Orders helper file."""

import logging
from decimal import Decimal

from django.db.models import Q
from elites_franchise_portal.debit.models import InventoryRecord
from elites_franchise_portal.orders.models import InstallmentsOrderItem, InstantOrderItem
from elites_franchise_portal.enterprise_mgt.models import EnterpriseSetupRule
from elites_franchise_portal.encounters.models import Encounter

LOGGER = logging.getLogger(__name__)


def process_order_transaction(order_transaction):
    """Process a transaction for an order."""

    order = order_transaction.order
    instant_order_items = InstantOrderItem.objects.filter(
        order=order_transaction.order, is_cleared=False)
    installment_order_items = InstallmentsOrderItem.objects.filter(
        order=order_transaction.order, is_cleared=False)
    enterprise_setup_rules = EnterpriseSetupRule.objects.get(
        enterprise=order_transaction.enterprise, is_active=True)
    default_inventory = enterprise_setup_rules.default_inventory
    audit_fields = {
        'created_by': order_transaction.created_by,
        'updated_by': order_transaction.updated_by,
        'enterprise': order_transaction.enterprise
        }

    if instant_order_items.exists():
        instant_order_items_totals = instant_order_items.values_list(
            'total_amount', flat=True)
        instant_order_items_total_amount = sum(instant_order_items_totals)
        if order_transaction.balance >= instant_order_items_total_amount:
            for instant_order_item in instant_order_items:
                instant_order_item.quantity_awaiting_clearance = 0
                instant_order_item.quantity_cleared = instant_order_item.quantity
                instant_order_item.confirmation_status = "CONFIRMED"
                instant_order_item.is_cleared = True
                instant_order_item.payment_status = "FULLY PAID"
                instant_order_item.amount_paid = instant_order_item.total_amount
                instant_order_item.payment_is_processed = True
                instant_order_item.save()

            new_balance = Decimal(order_transaction.balance) - Decimal(instant_order_items_total_amount)
            order_transaction.balance = new_balance
            order_transaction.__class__.objects.filter(id=order_transaction.id).update(balance=new_balance)
            instant_order_item.refresh_from_db()
            inventory_item = instant_order_item.cart_item.catalog_item.inventory_item
            InventoryRecord.objects.create(
                inventory=default_inventory, inventory_item=inventory_item,
                quantity_recorded=instant_order_item.quantity_cleared,
                unit_price=instant_order_item.unit_price,
                quantity_sold=instant_order_item.quantity_cleared,
                record_type='REMOVE', removal_type='SALES', **audit_fields)
            order.instant_order_total = instant_order_items_totals
            order.save()

        else:
            LOGGER.info('The available amount cannot fullfill the order')

        if not installment_order_items.exists():
            order.is_cleared = True
            order.is_processed = True
            order.save()

    if installment_order_items.exists():
        allocated_inventory = enterprise_setup_rules.allocated_inventory
        installment_order_items_totals = installment_order_items.values_list(
            'total_amount', flat=True)
        installment_order_items_total_amount = sum(installment_order_items_totals)

        if order_transaction.balance < installment_order_items_total_amount:
            installment_order_items = installment_order_items
            for installment_order_item in installment_order_items:
                encounter = Encounter.objects.filter(order_guid=installment_order_item.order.id).first()
                catalog_item_id = installment_order_item.cart_item.catalog_item.id
                encounter_deposit = None

                for bill in encounter.billing:
                    if bill['catalog_item'] == str(catalog_item_id):
                        encounter_deposit = bill.get('deposit')
                        break

                if not installment_order_item.deposit_amount:
                    if encounter_deposit:
                        deposit_amount = encounter_deposit
                        installment_order_item.quantity_on_partial_deposit = installment_order_item.quantity
                        installment_order_item.deposit_amount = deposit_amount
                        installment_order_item.amount_paid = deposit_amount
                        installment_order_item.payment_status = 'DEPOSIT PAID'
                        installment_order_item.save()
                    else:
                        deposit_amount = order_transaction.balance if order_transaction.balance <= installment_order_item.total_amount else installment_order_item.total_amount    # noqa
                        installment_order_item.quantity_on_partial_deposit = installment_order_item.quantity
                        installment_order_item.deposit_amount = deposit_amount
                        installment_order_item.amount_paid = deposit_amount
                        installment_order_item.payment_status = 'DEPOSIT PAID'
                        installment_order_item.save()

                    new_balance = Decimal(float(order_transaction.balance) - float(deposit_amount))
                    order_transaction.balance = new_balance
                    order_transaction.__class__.objects.filter(id=order_transaction.id).update(balance=new_balance)

                    installment_order_item.refresh_from_db()
                    inventory_item = installment_order_item.cart_item.catalog_item.inventory_item
                    InventoryRecord.objects.create(
                        inventory=allocated_inventory, inventory_item=inventory_item,
                        quantity_recorded=installment_order_item.quantity_cleared,
                        unit_price=installment_order_item.unit_price,
                        record_type='ADD', **audit_fields)

                else:
                    LOGGER.info('Should process the amount as an installment')
                    pass

        else:
            LOGGER.info('The available amount can full the order as an instant order item')
            pass

    else:
        # Order is present but there are no order items
        LOGGER.info("Push the balance to Customer's wallet")
        pass

def refresh_order(order):
    from elites_franchise_portal.orders.models import (
        Cart, CartItem, InstallmentsOrderItem, InstantOrderItem)
    customer = order.customer
    InstantOrderItem.objects.filter(order=order)
    InstallmentsOrderItem.objects.filter(order=order)
    carts = Cart.objects.filter(
        Q(order_guid=order.id) | Q(cart_code=order.cart_code),
        enterprise=order.enterprise)

    if not customer.is_enterprise:
        carts.update(customer=customer)
    pass
    # Get all sales attached to this order
    # Get all the order items
    # Get all Order Transactions
    # Now Process This
