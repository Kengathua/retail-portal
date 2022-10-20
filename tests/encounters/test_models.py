"""Encounters models test file."""

from unittest import mock
from django.test import TestCase

from elites_franchise_portal.items.models import (
    Brand, BrandItemType, Category, Item, ItemModel, ItemType,
    ItemUnits, UnitsItemType, Units)
from elites_franchise_portal.debit.models import (
    Inventory, InventoryItem, InventoryInventoryItem,
    InventoryRecord)
from elites_franchise_portal.warehouses.models import (
    Warehouse)
from elites_franchise_portal.enterprises.models import Enterprise
from elites_franchise_portal.customers.models import Customer
from elites_franchise_portal.catalog.models import (
    Catalog, CatalogCatalogItem, CatalogItem)
from elites_franchise_portal.encounters.models import Encounter
from elites_franchise_portal.restrictions_mgt.models import EnterpriseSetupRules

from model_bakery import baker

MK_ROOT = 'elites_franchise_portal.encounters'


class TestEncounter(TestCase):
    """."""

    @mock.patch(MK_ROOT+'.tasks.process_customer_encounter.delay')
    def test_create_encounter(self, mock_process_customer_encounter):
        """."""
        franchise = baker.make(Enterprise, name='Elites Age Supermarket')
        enterprise_code = franchise.enterprise_code
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
            quantity_of_sale_units_per_purchase_unit=12, enterprise=enterprise_code)
        baker.make(
            ItemUnits, item=item2, sales_units=s_units, purchases_units=p_units,
            quantity_of_sale_units_per_purchase_unit=12, enterprise=enterprise_code)
        master_inventory = baker.make(
            Inventory, inventory_name='Elites Age Supermarket Working Stock Inventory',
            is_master=True, is_active=True, inventory_type='WORKING STOCK',
            enterprise=enterprise_code)
        available_inventory = baker.make(
            Inventory, inventory_name='Elites Age Supermarket Available Inventory',
            is_active=True, inventory_type='AVAILABLE', enterprise=enterprise_code)
        catalog = baker.make(
            Catalog, catalog_name='Elites Age Supermarket Standard Catalog',
            description='Standard Catalog', is_standard=True, enterprise=enterprise_code)
        receiving_warehouse = baker.make(
            Warehouse, warehouse_name='Elites Private Warehouse', is_default=True,
            enterprise=enterprise_code)
        baker.make(
            EnterpriseSetupRules, master_inventory=master_inventory,
            default_inventory=available_inventory, receiving_warehouse=receiving_warehouse,
            default_warehouse=receiving_warehouse, standard_catalog=catalog,
            default_catalog=catalog, is_active=True, enterprise=enterprise_code)
        inventory_item1 = baker.make(InventoryItem, item=item1, enterprise=enterprise_code)
        inventory_item2 = baker.make(InventoryItem, item=item2, enterprise=enterprise_code)
        baker.make(
            InventoryInventoryItem, inventory=master_inventory, inventory_item=inventory_item1)
        baker.make(
            InventoryInventoryItem, inventory=master_inventory, inventory_item=inventory_item2)
        baker.make(
            InventoryInventoryItem, inventory=available_inventory, inventory_item=inventory_item1)
        baker.make(
            InventoryInventoryItem, inventory=available_inventory, inventory_item=inventory_item2)
        baker.make(
            InventoryRecord, inventory=available_inventory, inventory_item=inventory_item1,
            record_type='ADD', quantity_recorded=2, unit_price=1500, enterprise=enterprise_code)
        baker.make(
            InventoryRecord, inventory=available_inventory, inventory_item=inventory_item2,
            record_type='ADD', quantity_recorded=2, unit_price=2000, enterprise=enterprise_code)
        catalog_item1 = baker.make(
            CatalogItem, inventory_item=inventory_item1, quantity=5, enterprise=enterprise_code)
        catalog_item2 = baker.make(
            CatalogItem, inventory_item=inventory_item2, quantity=6, enterprise=enterprise_code)
        baker.make(CatalogCatalogItem, catalog=catalog, catalog_item=catalog_item1)
        baker.make(CatalogCatalogItem, catalog=catalog, catalog_item=catalog_item2)
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

        mock_process_customer_encounter.assert_called_once_with(encounter.id)
