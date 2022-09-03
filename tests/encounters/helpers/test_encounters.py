"""Encounters helpers test file."""

import pytest
from unittest import mock

from elites_franchise_portal.items.models import (
    Brand, BrandItemType, Category, Item, ItemModel, ItemType,
    ItemUnits, UnitsItemType, Units)
from elites_franchise_portal.debit.models import (
    Inventory, InventoryItem, InventoryInventoryItem,
    InventoryRecord)
from elites_franchise_portal.debit.models import (
    Warehouse)
from elites_franchise_portal.orders.models import (
    Cart, CartItem, Order, InstantOrderItem, InstallmentsOrderItem,
    OrderTransaction)
from elites_franchise_portal.transactions.models import Transaction, Payment
from elites_franchise_portal.franchises.models import Franchise
from elites_franchise_portal.customers.models import Customer
from elites_franchise_portal.catalog.models import (
    Catalog, CatalogItem)
from elites_franchise_portal.encounters.models import Encounter

from model_bakery import baker

from elites_franchise_portal.encounters.tasks import process_customer_encounter
MK_ROOT = 'elites_franchise_portal.encounters'

pytestmark = pytest.mark.django_db


@mock.patch(MK_ROOT+'.tasks.process_customer_encounter.delay')
def test_process_customer_encounter(mock_process_customer_encounter):
    """."""
    franchise = baker.make(Franchise, name='Elites Age Supermarket')
    franchise_code = franchise.elites_code
    cat = baker.make(
        Category, category_name='Cat One',
        franchise=franchise_code)
    item_type = baker.make(
        ItemType, category=cat, type_name='Cooker',
        franchise=franchise_code)
    brand = baker.make(
        Brand, brand_name='Samsung', franchise=franchise_code)
    baker.make(
        BrandItemType, brand=brand, item_type=item_type,
        franchise=franchise_code)
    item_model1 = baker.make(
        ItemModel, brand=brand, item_type=item_type, model_name='GE731K-B SUT',
        franchise=franchise_code)
    item_model2 = baker.make(
        ItemModel, brand=brand, item_type=item_type, model_name='WRTHY46-G DAT',
        franchise=franchise_code)
    baker.make(
        Warehouse, warehouse_name='Elites Private Warehouse', warehouse_type='PRIVATE',
        franchise=franchise_code)
    baker.make(
        Inventory, inventory_name='Elites Age Supermarket Working Stock Inventory',
        is_master=True, is_active=True, inventory_type='WORKING STOCK',
        franchise=franchise_code)
    available_inventory = baker.make(
        Inventory, inventory_name='Elites Age Supermarket Available Inventory',
        is_active=True, inventory_type='AVAILABLE', franchise=franchise_code)
    baker.make(
        Catalog, name='Elites Age Supermarket Standard Catalog',
        description='Standard Catalog', is_standard=True,
        franchise=franchise_code)
    item1 = baker.make(
        Item, item_model=item_model1, barcode='83838388383', make_year=2020,
        franchise=franchise_code)
    item1.activate()
    item2 = baker.make(
        Item, item_model=item_model2, barcode='83838388383', make_year=2020,
        franchise=franchise_code)
    item2.activate()
    s_units = baker.make(Units, units_name='packet', franchise=franchise_code)
    baker.make(UnitsItemType, item_type=item_type, units=s_units, franchise=franchise_code)
    s_units.item_types.set([item_type])
    s_units.save()
    p_units = baker.make(Units, units_name='Dozen', franchise=franchise_code)
    baker.make(UnitsItemType, item_type=item_type, units=p_units, franchise=franchise_code)
    p_units.item_types.set([item_type])
    p_units.save()
    baker.make(
        ItemUnits, item=item1, sales_units=s_units, purchases_units=p_units,
        items_per_purchase_unit=12, franchise=franchise_code)
    baker.make(
        ItemUnits, item=item2, sales_units=s_units, purchases_units=p_units,
        items_per_purchase_unit=12, franchise=franchise_code)
    inventory_item1 = InventoryItem.objects.get(item=item1, franchise=franchise_code)
    inventory_item2 = InventoryItem.objects.get(item=item2, franchise=franchise_code)
    baker.make(
        InventoryInventoryItem, inventory=available_inventory, inventory_item=inventory_item1)
    baker.make(
        InventoryInventoryItem, inventory=available_inventory, inventory_item=inventory_item2)
    baker.make(
        InventoryRecord, inventory=available_inventory, inventory_item=inventory_item1,
        record_type='ADD', quantity_recorded=2, unit_price=1500, franchise=franchise_code)
    baker.make(
        InventoryRecord, inventory=available_inventory, inventory_item=inventory_item2,
        record_type='ADD', quantity_recorded=2, unit_price=2000, franchise=franchise_code)
    baker.make(
        Catalog, name='Elites Age Supermarket Standard Catalog',
        description='Standard Catalog', is_standard=True,
        franchise=franchise_code)
    catalog_item1 = baker.make(
        CatalogItem, inventory_item=inventory_item1, franchise=franchise_code)
    catalog_item2 = baker.make(
        CatalogItem, inventory_item=inventory_item2, franchise=franchise_code)
    customer = baker.make(
        Customer, customer_number=9876, first_name='John',
        last_name='Wick', other_names='Baba Yaga',
        phone_no='+254712345678', email='johnwick@parabellum.com')
    billing = [
        {
            'catalog_item': str(catalog_item1.id),
            'item_name': catalog_item1.inventory_item.item.item_name,
            'quantity': 2,
            'unit_price': 1600,
            'total': 3200,
            'sale_type': 'INSTANT'
        },
        {
            'catalog_item': str(catalog_item2.id),
            'item_name': catalog_item2.inventory_item.item.item_name,
            'quantity': 3,
            'unit_price': 2200,
            'total': 6600,
            'sale_type': 'INSTALLMENT'
        },
    ]
    payments = [{'means': 'CASH', 'amount': 5000, }]

    encounter = baker.make(
        Encounter, customer=customer, billing=billing, payments=payments,
        franchise=franchise_code)

    mock_process_customer_encounter.assert_called_once_with(encounter.id)
    process_customer_encounter(encounter.id)
    assert Cart.objects.count() == 1
    assert CartItem.objects.count() == 2
    assert CartItem.objects.filter(
        is_installment=True, catalog_item=catalog_item2).count() == 1
    assert CartItem.objects.filter(
        is_installment=False, catalog_item=catalog_item1).count() == 1
    assert Order.objects.count() == 1
    order = Order.objects.first()
    assert InstallmentsOrderItem.objects.filter(
        cart_item__catalog_item=catalog_item2).count() == 1
    assert InstantOrderItem.objects.filter(
        cart_item__catalog_item=catalog_item1).count() == 1

    assert Payment.objects.count() == 1
    assert Transaction.objects.count() == 1
    assert OrderTransaction.objects.count() == 1
    assert OrderTransaction.objects.first().order == order
