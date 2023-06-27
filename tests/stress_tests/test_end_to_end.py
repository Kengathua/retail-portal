"""."""

import pytest
from django.test import TestCase
from django.core.exceptions import ValidationError

from elites_retail_portal.encounters.models import Encounter
from elites_retail_portal.enterprises.models import Enterprise
from elites_retail_portal.items.models import (
    Brand, BrandItemType, Category, Item, ItemModel, ItemType,
    ItemUnits, UnitsItemType, Units)
from elites_retail_portal.debit.models import (
    InventoryItem, Inventory, InventoryInventoryItem, InventoryRecord)
from elites_retail_portal.catalog.models import (
    Section, Catalog, CatalogItem, CatalogCatalogItem)
from elites_retail_portal.orders.models import (
    Cart, Order, OrderTransaction, InstantOrderItem, InstallmentsOrderItem, Installment)
from elites_retail_portal.customers.models import Customer
from elites_retail_portal.warehouses.models import Warehouse
from elites_retail_portal.credit.models import Purchase, PurchaseItem
from elites_retail_portal.transactions.models import (
    Payment, Transaction)
from elites_retail_portal.enterprise_mgt.models import (
    EnterpriseSetupRule, EnterpriseSetupRuleInventory,
    EnterpriseSetupRuleCatalog, EnterpriseSetupRuleWarehouse)

from model_bakery import baker
from model_bakery.recipe import Recipe


class TesTEndToEnd(TestCase):
    """."""

    def test_create_reference_catalog(self):
        """Test End To End for daily recurrent instances."""

        enterprise = baker.make(Enterprise, name='Elites Age Supermarket')
        enterprise_code = enterprise.enterprise_code
        cat = baker.make(
            Category, category_name='Cat One',
            enterprise=enterprise_code)
        item_type = baker.make(
            ItemType, category=cat, type_name='Cooker',
            enterprise=enterprise_code)
        brand = baker.make(
            Brand, brand_name='Samsung', enterprise=enterprise_code)
        baker.make(
            BrandItemType, brand=brand, item_type=item_type,
            enterprise=enterprise_code)
        item_model1 = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731K-B SUT',
            enterprise=enterprise_code)
        item_model2 = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='WRTHY46-G DAT',
            enterprise=enterprise_code)
        baker.make(
            Catalog, catalog_name='Elites Age Supermarket Standard Catalog',
            description='Standard Catalog', is_standard=True,
            enterprise=enterprise_code)
        item1 = baker.make(
            Item, item_model=item_model1, barcode='83838388383', make_year=2020,
            enterprise=enterprise_code)
        item2 = baker.make(
            Item, item_model=item_model2, barcode='83838388383', make_year=2020,
            enterprise=enterprise_code)
        s_units = baker.make(Units, units_name='packet', enterprise=enterprise_code)
        baker.make(UnitsItemType, item_type=item_type, units=s_units, enterprise=enterprise_code)
        s_units.item_types.set([item_type])
        s_units.save()
        p_units = baker.make(Units, units_name='Dozen', enterprise=enterprise_code)
        baker.make(UnitsItemType, item_type=item_type, units=p_units, enterprise=enterprise_code)
        p_units.item_types.set([item_type])
        p_units.save()
        baker.make(
            ItemUnits, item=item1, sales_units=s_units, purchases_units=p_units,
            quantity_of_sale_units_per_purchase_unit=1, enterprise=enterprise_code)
        baker.make(
            ItemUnits, item=item2, sales_units=s_units, purchases_units=p_units,
            quantity_of_sale_units_per_purchase_unit=12, enterprise=enterprise_code)
        inventory = baker.make(
            Inventory, inventory_name='Elites Age Supermarket Available Inventory',
            is_default=True, is_master=True,
            is_active=True, inventory_type='AVAILABLE', enterprise=enterprise_code)
        allocated_inventory = baker.make(
            Inventory, inventory_name='Elites Age Supermarket Allocated Inventory',
            is_active=True, inventory_type='ALLOCATED', enterprise=enterprise_code)
        catalog = baker.make(
            Catalog, catalog_name='Elites Age Supermarket Standard Catalog',
            is_default=True,
            description='Standard Catalog', is_standard=True, enterprise=enterprise_code)
        warehouse = baker.make(
            Warehouse, warehouse_name='Elites Private Warehouse', is_default=True,
            is_receiving=True,
            enterprise=enterprise_code)
        rule = baker.make(
            EnterpriseSetupRule, name='Elites Age', is_active=True, enterprise=enterprise_code)
        baker.make(
            EnterpriseSetupRuleInventory, rule=rule, inventory=inventory,
            enterprise=enterprise_code)
        baker.make(
            EnterpriseSetupRuleInventory, rule=rule, inventory=allocated_inventory,
            enterprise=enterprise_code)
        baker.make(
            EnterpriseSetupRuleWarehouse, rule=rule, warehouse=warehouse,
            enterprise=enterprise_code)
        baker.make(
            EnterpriseSetupRuleCatalog, rule=rule, catalog=catalog,
            enterprise=enterprise_code)
        inventory_item1 = baker.make(InventoryItem, item=item1, enterprise=enterprise_code)
        inventory_item2 = baker.make(InventoryItem, item=item2, enterprise=enterprise_code)
        item1.activate()
        item2.activate()
        baker.make(
            InventoryInventoryItem, inventory=inventory, inventory_item=inventory_item1)
        baker.make(
            InventoryInventoryItem, inventory=inventory, inventory_item=inventory_item2)
        baker.make(
            InventoryInventoryItem, inventory=inventory, inventory_item=inventory_item1)
        baker.make(
            InventoryInventoryItem, inventory=inventory, inventory_item=inventory_item2)
        baker.make(
            InventoryInventoryItem, inventory=allocated_inventory, inventory_item=inventory_item1)
        baker.make(
            InventoryInventoryItem, inventory=allocated_inventory, inventory_item=inventory_item2)
        baker.make(
            InventoryRecord, inventory=inventory, inventory_item=inventory_item1,
            record_type='ADD', quantity_recorded=4, unit_price=1500, enterprise=enterprise_code)
        baker.make(
            InventoryRecord, inventory=inventory, inventory_item=inventory_item2,
            record_type='ADD', quantity_recorded=5, unit_price=2000, enterprise=enterprise_code)
        section = baker.make(Section, section_name='KITCHEN', enterprise=enterprise_code)
        catalog_item1 = baker.make(
            CatalogItem, section=section, inventory_item=inventory_item1, enterprise=enterprise_code)
        catalog_item2 = baker.make(
            CatalogItem, section=section, inventory_item=inventory_item2, enterprise=enterprise_code)

        catalog_item1.refresh_from_db()
        catalog_item2.refresh_from_db()
        assert catalog_item1.quantity == 4
        assert catalog_item2.quantity == 5

        baker.make(CatalogCatalogItem, catalog=catalog, catalog_item=catalog_item1)
        baker.make(CatalogCatalogItem, catalog=catalog, catalog_item=catalog_item2)

        customer = baker.make(
            Customer, customer_number=9876, first_name='John', gender='MALE',
            last_name='Wick', other_names='Baba Yaga', enterprise=enterprise_code,
            phone_no='+254712345678', email='johnwick@parabellum.com')
        billing = [
            {
                'catalog_item': str(catalog_item1.id),
                'item_name': catalog_item1.inventory_item.item.item_name,
                'quantity': 2,
                'unit_price': 1600,
                'total': 3200,
                'deposit': None,
                'sale_type': 'INSTANT'
            },
            {
                'catalog_item': str(catalog_item2.id),
                'item_name': catalog_item2.inventory_item.item.item_name,
                'quantity': 3,
                'unit_price': 2200,
                'deposit': 3000,
                'total': 6600,
                'sale_type': 'INSTALLMENT'
            },
        ]
        payments = [
            {
                'means': 'CASH',
                'amount': 5000
            },
            {
                'means': 'MPESA TILL',
                'amount': 2000
            }
        ]

        encounter = baker.make(
            Encounter, customer=customer, billing=billing, payments=payments,
            submitted_amount=7000, enterprise=enterprise_code)

        assert encounter.balance_amount == 7000 - (3000+3200) == 800

        assert Encounter.objects.count() == 1
        assert Cart.objects.count() == 1
        assert Order.objects.count() == 1
        assert Payment.objects.count() == 2
        assert Transaction.objects.count() == 1
        assert OrderTransaction.objects.count() == 1
        assert InstantOrderItem.objects.count() == 1
        assert InstallmentsOrderItem.objects.count() == 1

        transaction1 = Transaction.objects.first()
        assert transaction1.amount == 6200
        assert transaction1.balance == 6200

        instant_order_item = InstantOrderItem.objects.first()
        installments_order_item = InstallmentsOrderItem.objects.first()
        order1 = installments_order_item.order

        assert instant_order_item.is_cleared
        assert instant_order_item.payment_is_processed
        assert instant_order_item.payment_status == 'FULLY PAID'
        assert instant_order_item.quantity == 2
        assert instant_order_item.quantity_awaiting_clearance == 0
        assert instant_order_item.quantity_cleared == 2
        assert instant_order_item.unit_price == 1600
        assert instant_order_item.total_amount == 3200

        assert installments_order_item.amount_due == 3600
        assert installments_order_item.amount_paid == 3000
        assert installments_order_item.confirmation_status == 'PENDING'
        assert installments_order_item.deposit_amount == 3000
        assert not installments_order_item.is_cleared
        assert not installments_order_item.payment_is_processed

        assert installments_order_item.quantity == 3
        assert installments_order_item.quantity_awaiting_clearance == 3
        assert installments_order_item.quantity_cleared == 0
        assert installments_order_item.quantity_on_full_deposit == 0

        assert installments_order_item.quantity_on_partial_deposit == 3
        assert installments_order_item.quantity_without_deposit == 0
        assert installments_order_item.unit_price == 2200
        assert installments_order_item.total_amount == 6600

        catalog_item1.refresh_from_db()
        catalog_item2.refresh_from_db()

        assert catalog_item1.quantity == 4-2 == 2
        assert catalog_item2.quantity == 5

        supplier = baker.make(Enterprise, name='LG Suppplier', enterprise_type='SUPPLIER')
        purchase = baker.make(
            Purchase, supplier=supplier, enterprise=enterprise_code)
        baker.make(
            PurchaseItem, purchase=purchase, item=item1, quantity_purchased=5,
            total_cost=7500, recommended_retail_price=2000, quantity_to_inventory=5,
            quantity_to_inventory_on_display=5, enterprise=enterprise_code)
        purchase_item = baker.make(
            PurchaseItem, purchase=purchase, item=item2, quantity_purchased=6,
            total_cost=12000, recommended_retail_price=2500, quantity_to_inventory=6,
            quantity_to_inventory_on_display=6, enterprise=enterprise_code)

        catalog_item1.refresh_from_db()
        catalog_item2.refresh_from_db()

        assert purchase_item.quantity_purchased == 6
        assert purchase_item.sale_units_purchased == 72
        assert purchase_item.total_quantity_puchased == 72
        assert purchase_item.total_cost == 12000.00
        assert float(purchase_item.unit_cost) == float(format((12000 / 72), ".2f")) == 166.67
        assert catalog_item1.quantity == 2 + 5 == 7
        assert catalog_item2.quantity == 5 + 72 == 77

        payment2 = baker.make(
            Payment, paid_amount=400, is_installment=True, enterprise=enterprise_code)
        transaction2 = baker.make(
            Transaction, amount=payment2.final_amount, enterprise=enterprise_code)
        payment2.transaction_guid = transaction2.id
        order_transaction2 = baker.make(
            OrderTransaction, transaction=transaction2, order=installments_order_item.order,
            amount=transaction2.amount, enterprise=enterprise_code)
        installment1 = baker.make(
            Installment, order_transaction=order_transaction2, is_direct_installment=True,
            amount=order_transaction2.amount, installment_item=installments_order_item,
            enterprise=enterprise_code)
        installment1.process_installment()

        assert installment1
        installments_order_item.refresh_from_db()
        assert installments_order_item.amount_paid == 3000 + 400 == 3400
        assert installments_order_item.quantity == 3
        assert installments_order_item.quantity_cleared == 1
        assert installments_order_item.quantity_awaiting_clearance == 2

        order1.refresh_from_db()
        assert not order1.is_cleared

        payment3 = baker.make(
            Payment, paid_amount=999, is_installment=True, enterprise=enterprise_code)
        transaction3 = baker.make(
            Transaction, amount=payment3.final_amount, enterprise=enterprise_code)
        payment3.transaction_guid = transaction3.id
        order_transaction3 = baker.make(
            OrderTransaction, transaction=transaction3, order=installments_order_item.order,
            amount=transaction3.amount, enterprise=enterprise_code)
        installment2 = baker.make(
            Installment, order_transaction=order_transaction3, is_direct_installment=True,
            amount=order_transaction3.amount, installment_item=installments_order_item,
            enterprise=enterprise_code)
        installment2.process_installment()

        assert installment2
        installments_order_item.refresh_from_db()
        assert installments_order_item.amount_paid == 3400 + 999 == 4399
        assert installments_order_item.quantity == 3
        assert installments_order_item.quantity_cleared == 1
        assert installments_order_item.quantity_awaiting_clearance == 2

        order1.refresh_from_db()
        assert not order1.is_cleared

        payment4 = baker.make(
            Payment, paid_amount=1, is_installment=True, enterprise=enterprise_code)
        transaction4 = baker.make(
            Transaction, amount=payment4.final_amount, enterprise=enterprise_code)
        payment4.transaction_guid = transaction4.id
        order_transaction4 = baker.make(
            OrderTransaction, transaction=transaction4, order=installments_order_item.order,
            amount=transaction4.amount, enterprise=enterprise_code)
        installment3 = baker.make(
            Installment, order_transaction=order_transaction4, is_direct_installment=True,
            amount=order_transaction4.amount, installment_item=installments_order_item,
            enterprise=enterprise_code)
        installment3.process_installment()

        assert installment3
        installments_order_item.refresh_from_db()
        assert installments_order_item.amount_paid == 4399 + 1 == 4400
        assert installments_order_item.quantity == 3

        assert installments_order_item.quantity_cleared == 2
        assert installments_order_item.quantity_awaiting_clearance == 1

        order1.refresh_from_db()
        assert not order1.is_cleared

        payment5 = baker.make(
            Payment, paid_amount=2200, is_installment=True, enterprise=enterprise_code)
        transaction5 = baker.make(
            Transaction, amount=payment5.final_amount, enterprise=enterprise_code)
        payment5.transaction_guid = transaction5.id
        order_transaction5 = baker.make(
            OrderTransaction, transaction=transaction5, order=installments_order_item.order,
            amount=transaction5.amount, enterprise=enterprise_code)
        installment4 = baker.make(
            Installment, order_transaction=order_transaction5, is_direct_installment=True,
            amount=order_transaction5.amount, installment_item=installments_order_item,
            enterprise=enterprise_code)
        installment4.process_installment()

        assert installment4
        installments_order_item.refresh_from_db()
        assert installments_order_item.amount_paid == 4400 + 2200 == 6600
        assert installments_order_item.quantity == 3
        assert installments_order_item.quantity_cleared == 3
        assert installments_order_item.quantity_awaiting_clearance == 0

        order1.refresh_from_db()
        assert order1.is_cleared

        catalog_item1.refresh_from_db()
        catalog_item2.refresh_from_db()

        assert catalog_item1.quantity == 2 + 5 == 7
        assert catalog_item2.quantity == 77 - 3 == 74

        payment6 = baker.make(
            Payment, paid_amount=1, is_installment=True, enterprise=enterprise_code)
        transaction6 = baker.make(
            Transaction, amount=payment6.final_amount, enterprise=enterprise_code)
        payment6.transaction_guid = transaction6.id
        order_transaction6 = baker.make(
            OrderTransaction, transaction=transaction6, order=installments_order_item.order,
            amount=transaction6.amount, enterprise=enterprise_code)
        installment5_recipe = Recipe(
            Installment, order_transaction=order_transaction6, is_direct_installment=True,
            amount=order_transaction6.amount, installment_item=installments_order_item,
            enterprise=enterprise_code)

        with pytest.raises(ValidationError) as ve:
            installment5_recipe.make()

        msg = 'Please select a different item to process installments for John Baba Yaga Wick. '\
            'His SAMSUNG WRTHY46-G DAT COOKER is already cleared'
        assert msg in ve.value.messages

        installments_order_item.refresh_from_db()
        assert installments_order_item.quantity == 3
        assert installments_order_item.quantity_cleared == 3
        assert installments_order_item.quantity_awaiting_clearance == 0

        order1.refresh_from_db()
        assert order1.is_cleared
        assert order1.is_processed
