"""."""

import uuid
import pytest
from django.test import TestCase
from django.core.exceptions import ValidationError

from elites_franchise_portal.enterprises.models import Enterprise
from elites_franchise_portal.items.models import (
    Brand, BrandItemType, Category, Item, ItemModel, ItemType,
    ItemUnits, UnitsItemType, Units)
from elites_franchise_portal.debit.models import (
    Inventory, InventoryItem, InventoryRecord)
from elites_franchise_portal.warehouses.models import (
    Warehouse, WarehouseItem, WarehouseRecord)
from elites_franchise_portal.catalog.models import CatalogItem, Section, Catalog, CatalogCatalogItem, CatalogItemAuditLog
from elites_franchise_portal.debit.models.inventory import InventoryInventoryItem
from elites_franchise_portal.enterprise_mgt.models import (
    EnterpriseSetupRule, EnterpriseSetupRuleInventory, EnterpriseSetupRuleCatalog, EnterpriseSetupRuleWarehouse)

from model_bakery import baker
from model_bakery.recipe import Recipe


class TestInventory(TestCase):
    """."""

    def test_create_inventory(self):
        """."""
        franchise = baker.make(Enterprise, name='Elites Age Supermarket')
        enterprise_code = franchise.enterprise_code
        inventory = baker.make(
            Inventory, inventory_name='Elites Age Supermarket Working Stock Inventory',
            inventory_type='WORKING STOCK', enterprise=enterprise_code)

        assert inventory
        assert Inventory.objects.count() == 1

    def test_validate_unique_active_master_inventory_for_franchise(self):
        franchise = baker.make(Enterprise, name='Elites Age Supermarket')
        enterprise_code = franchise.enterprise_code
        baker.make(
            Inventory, inventory_name='Elites Age Supermarket Working Stock Inventory',
            is_master=True, is_active=True, inventory_type='WORKING STOCK',
            enterprise=enterprise_code)
        inventory = Recipe(
            Inventory, inventory_name='Elites Age Supermarket Inventory',
            is_master=True, is_active=True, inventory_type='WORKING STOCK',
            enterprise=enterprise_code)

        with pytest.raises(ValidationError) as ve:
            inventory.make()
        msg = 'You can only have one active master inventory'
        assert msg in ve.value.messages

    def test_validate_unique_active_available_inventory_for_franchise(self):
        franchise = baker.make(Enterprise, name='Elites Age Supermarket')
        enterprise_code = franchise.enterprise_code
        inventory1 = baker.make(
            Inventory, inventory_name='Elites Age Supermarket Available Inventory',
            is_active=True, inventory_type='AVAILABLE', enterprise=enterprise_code)
        inventory2 = Recipe(
            Inventory, inventory_name='Elites Age Supermarket Available Inventory',
            is_active=True, inventory_type='AVAILABLE', enterprise=enterprise_code)
        with pytest.raises(ValidationError) as ve:
            inventory2.make()
        msg = 'You can only have one active Available inventory'
        assert msg in ve.value.messages
        assert inventory1

    def test_validate_unique_active_allocated_inventory_for_franchise(self):
        franchise = baker.make(Enterprise, name='Elites Age Supermarket')
        enterprise_code = franchise.enterprise_code
        baker.make(
            Inventory, inventory_name='Elites Age Supermarket Allocated Inventory',
            is_active=True, inventory_type='ALLOCATED', enterprise=enterprise_code)
        inventory = Recipe(
            Inventory, inventory_name='Elites Age Supermarket Allocated Inventory',
            is_active=True, inventory_type='ALLOCATED', enterprise=enterprise_code)
        with pytest.raises(ValidationError) as ve:
            inventory.make()
        msg = 'You can only have one active Allocated inventory'
        assert msg in ve.value.messages


class TestInventoryItem(TestCase):
    """."""

    def test_create_inventory_item(self):
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
        item_model = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731K-B SUT',
            enterprise=enterprise_code)
        item = baker.make(
            Item, item_model=item_model, barcode='83838388383', make_year=2020,
            enterprise=enterprise_code)
        inventory_item = baker.make(InventoryItem, item=item, enterprise=enterprise_code)
        assert inventory_item
        assert InventoryItem.objects.count() == 1


class TestInventoryRecord(TestCase):
    """."""

    def test_create_inventory_record(self):
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
        item_model = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731K-B SUT',
            enterprise=enterprise_code)
        item = baker.make(
            Item, item_model=item_model, barcode='83838388383', make_year=2020,
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
            ItemUnits, item=item, sales_units=s_units, purchases_units=p_units,
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
        warehouse = baker.make(
            Warehouse, warehouse_name='Elites Private Warehouse', is_default=True,
            enterprise=enterprise_code)
        rule = baker.make(
            EnterpriseSetupRule, name='Elite Age Rules', is_default=True,
            is_active=True, enterprise=enterprise_code)
        baker.make(EnterpriseSetupRuleInventory, rule=rule, inventory=master_inventory)
        baker.make(EnterpriseSetupRuleInventory, rule=rule, inventory=available_inventory)
        baker.make(EnterpriseSetupRuleWarehouse, rule=rule, warehouse=warehouse)
        baker.make(EnterpriseSetupRuleCatalog, rule=rule, catalog=catalog)
        inventory_item = baker.make(InventoryItem, item=item, enterprise=enterprise_code)
        baker.make(
            InventoryInventoryItem, inventory=master_inventory, inventory_item=inventory_item)
        baker.make(
            InventoryInventoryItem, inventory=available_inventory, inventory_item=inventory_item)
        record1 = baker.make(
            InventoryRecord, inventory=available_inventory, inventory_item=inventory_item,
            record_type='ADD', quantity_recorded=15, unit_price=300, enterprise=enterprise_code)

        assert record1
        assert record1.opening_stock_quantity == 0.0
        assert record1.opening_stock_total_amount == 0.0
        assert record1.closing_stock_quantity == 15.0
        assert record1.total_amount_recorded == 4500.0
        assert record1.closing_stock_total_amount == 4500.0
        assert InventoryRecord.objects.filter(inventory=available_inventory).count() == 1

        record2 = baker.make(
            InventoryRecord, inventory=available_inventory, inventory_item=inventory_item,
            record_type='ADD', quantity_recorded=10, unit_price=300, enterprise=enterprise_code)
        assert record2
        assert record2.opening_stock_quantity == 15.0
        assert record2.opening_stock_total_amount == 4500.0
        assert record2.closing_stock_quantity == 25.0
        assert record2.total_amount_recorded == 3000.0
        assert record2.closing_stock_total_amount == 7500.0

    def test_catalog_item_updated_after_adding_inventory_record(self):
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
        item_model = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731K-B SUT',
            enterprise=enterprise_code)
        item = baker.make(
            Item, item_model=item_model, barcode='83838388383', make_year=2020,
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
            ItemUnits, item=item, sales_units=s_units, purchases_units=p_units,
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
        warehouse = baker.make(
            Warehouse, warehouse_name='Elites Private Warehouse', is_default=True,
            enterprise=enterprise_code)
        rule = baker.make(
            EnterpriseSetupRule, name='Elite Age Rules', is_default=True,
            is_active=True, enterprise=enterprise_code)
        baker.make(EnterpriseSetupRuleInventory, rule=rule, inventory=master_inventory)
        baker.make(EnterpriseSetupRuleInventory, rule=rule, inventory=available_inventory)
        baker.make(EnterpriseSetupRuleWarehouse, rule=rule, warehouse=warehouse)
        baker.make(EnterpriseSetupRuleCatalog, rule=rule, catalog=catalog)
        inventory_item = baker.make(InventoryItem, item=item, enterprise=enterprise_code)
        baker.make(
            InventoryInventoryItem, inventory=master_inventory, inventory_item=inventory_item)
        baker.make(
            InventoryInventoryItem, inventory=available_inventory, inventory_item=inventory_item)
        section = baker.make(Section, section_name='Section A')
        inventory_item.check_item_in_catalog_items(section)
        catalog_item = CatalogItem.objects.get(
            inventory_item=inventory_item, enterprise=inventory_item.enterprise)
        baker.make(
            CatalogCatalogItem, catalog=catalog, catalog_item=catalog_item,
            enterprise=enterprise_code)
        assert catalog_item.marked_price == 0
        assert catalog_item.quantity == 0

        record1 = baker.make(
            InventoryRecord, inventory=available_inventory, inventory_item=inventory_item,
            record_type='ADD', quantity_recorded=15, unit_price=300, enterprise=enterprise_code)
        catalog_item.refresh_from_db()
        assert CatalogItem.objects.count() == 1
        assert catalog_item.marked_price == record1.unit_price == 300
        assert catalog_item.quantity == record1.quantity_recorded == 15

        record2 = baker.make(
            InventoryRecord, inventory=available_inventory, inventory_item=inventory_item,
            record_type='ADD', quantity_recorded=15, unit_price=370, enterprise=enterprise_code)
        expected_total = record1.quantity_recorded + record2.quantity_recorded
        catalog_item.refresh_from_db()
        assert CatalogItem.objects.count() == 1
        assert catalog_item.marked_price == record2.unit_price == 370
        assert catalog_item.quantity == expected_total == 30

        record1.save()
        catalog_item.refresh_from_db()
        assert CatalogItem.objects.count() == 1
        assert catalog_item.marked_price == record2.unit_price == 370
        assert catalog_item.quantity == expected_total == 30

        record1.quantity_recorded = 10
        record1.unit_price = 330
        expected_total = expected_total - 5
        record1.save()
        catalog_item.refresh_from_db()
        assert CatalogItem.objects.count() == 1
        assert catalog_item.marked_price == record2.unit_price == 370
        assert catalog_item.quantity == expected_total == 25

        record2.quantity_recorded = 18
        expected_total = expected_total + 3
        record2.unit_price = 400
        record2.save()
        catalog_item.refresh_from_db()
        assert CatalogItem.objects.count() == 1
        assert catalog_item.marked_price == record2.unit_price == 400
        assert catalog_item.quantity == expected_total == 28

        record3 = baker.make(
            InventoryRecord, inventory=available_inventory, inventory_item=inventory_item,
            record_type='ADD', quantity_recorded=20, unit_price=320, enterprise=enterprise_code)
        expected_total = record1.quantity_recorded + record2.quantity_recorded + record3.quantity_recorded  # noqa
        catalog_item.refresh_from_db()
        assert CatalogItem.objects.count() == 1
        assert catalog_item.marked_price == record3.unit_price == 320
        assert catalog_item.quantity == expected_total == 48

        # assert CatalogItemAuditLog.objects.filter().latest('created_on').quantity_after == 48


    def test_fail_remove_from_empty_inventory(self):
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
        item_model = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731K-B SUT',
            enterprise=enterprise_code)
        item = baker.make(
            Item, item_model=item_model, barcode='83838388383', make_year=2020,
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
            ItemUnits, item=item, sales_units=s_units, purchases_units=p_units,
            quantity_of_sale_units_per_purchase_unit=12, enterprise=enterprise_code)
        master_inventory = baker.make(
            Inventory, inventory_name='Elites Age Supermarket Working Stock Inventory',
            is_master=True, is_active=True, inventory_type='WORKING STOCK',
            enterprise=enterprise_code)
        available_inventory = baker.make(
            Inventory, inventory_name='Elites Age Supermarket Available Inventory',
            is_active=True, inventory_type='AVAILABLE', enterprise=enterprise_code)
        inventory_item = baker.make(InventoryItem, item=item, enterprise=enterprise_code)
        baker.make(
            InventoryInventoryItem, inventory=master_inventory, inventory_item=inventory_item)
        baker.make(
            InventoryInventoryItem, inventory=available_inventory, inventory_item=inventory_item)
        record_recipe = Recipe(
            InventoryRecord, inventory=available_inventory, inventory_item=inventory_item,
            record_type='REMOVE', quantity_recorded=15, unit_price=300, enterprise=enterprise_code)

        with pytest.raises(ValidationError) as ve:
            record_recipe.make()
        msg = 'You are trying to remove 15.0 items of SAMSUNG GE731K-B SUT COOKER '\
        'and the Elites Age Supermarket Available Inventory has 0 items'
        assert msg in ve.value.messages

    def test_remove_from_inventory(self):
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
        item_model = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731K-B SUT',
            enterprise=enterprise_code)
        item = baker.make(
            Item, item_model=item_model, barcode='83838388383', make_year=2020,
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
            ItemUnits, item=item, sales_units=s_units, purchases_units=p_units,
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
            EnterpriseSetupRule, master_inventory=master_inventory,
            default_inventory=available_inventory, receiving_warehouse=receiving_warehouse,
            default_warehouse=receiving_warehouse, standard_catalog=catalog,
            default_catalog=catalog, is_active=True, enterprise=enterprise_code)
        inventory_item = baker.make(InventoryItem, item=item, enterprise=enterprise_code)
        baker.make(
            InventoryInventoryItem, inventory=master_inventory, inventory_item=inventory_item)
        baker.make(
            InventoryInventoryItem, inventory=available_inventory, inventory_item=inventory_item)
        section = baker.make(Section, section_name='Section A')
        inventory_item.check_item_in_catalog_items(section)
        catalog_item = CatalogItem.objects.get(
            inventory_item=inventory_item, enterprise=enterprise_code)
        baker.make(
            CatalogCatalogItem, catalog=catalog, catalog_item=catalog_item,
            enterprise=enterprise_code)
        assert catalog_item.marked_price == 0
        assert catalog_item.quantity == 0

        record1 = baker.make(
            InventoryRecord, inventory=available_inventory, inventory_item=inventory_item,
            record_type='ADD', quantity_recorded=15, unit_price=300, enterprise=enterprise_code)
        catalog_item.refresh_from_db()
        assert CatalogItem.objects.count() == 1
        assert catalog_item.marked_price == record1.unit_price == 300
        assert catalog_item.quantity == record1.quantity_recorded == 15

        record2 = baker.make(
            InventoryRecord, inventory=available_inventory, inventory_item=inventory_item,
            record_type='REMOVE', removal_type='SALES', quantity_recorded=10, unit_price=320,
            enterprise=enterprise_code)
        expected_total = record1.quantity_recorded - record2.quantity_recorded
        catalog_item.refresh_from_db()
        assert catalog_item.marked_price == record1.unit_price == 300
        assert catalog_item.quantity == expected_total == 5

    def test_fail_remove_items_from_inventory_missing_removal_type(self):
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
        item_model = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731K-B SUT',
            enterprise=enterprise_code)
        item = baker.make(
            Item, item_model=item_model, barcode='83838388383', make_year=2020,
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
            ItemUnits, item=item, sales_units=s_units, purchases_units=p_units,
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
            EnterpriseSetupRule, master_inventory=master_inventory,
            default_inventory=available_inventory, receiving_warehouse=receiving_warehouse,
            default_warehouse=receiving_warehouse, standard_catalog=catalog,
            default_catalog=catalog, is_active=True, enterprise=enterprise_code)
        inventory_item = baker.make(InventoryItem, item=item, enterprise=enterprise_code)
        baker.make(
            InventoryInventoryItem, inventory=master_inventory, inventory_item=inventory_item)
        baker.make(
            InventoryInventoryItem, inventory=available_inventory, inventory_item=inventory_item)
        section = baker.make(Section, section_name='Section A')
        inventory_item.check_item_in_catalog_items(section)
        catalog_item = CatalogItem.objects.get(
            inventory_item=inventory_item, enterprise=enterprise_code)
        baker.make(
            CatalogCatalogItem, catalog=catalog, catalog_item=catalog_item,
            enterprise=enterprise_code)
        assert catalog_item.marked_price == 0
        assert catalog_item.quantity == 0

        baker.make(
            InventoryRecord, inventory=available_inventory, inventory_item=inventory_item,
            record_type='ADD', quantity_recorded=15, unit_price=300, enterprise=enterprise_code)

        record2_recipe = Recipe(
            InventoryRecord, inventory=available_inventory, inventory_item=inventory_item,
            record_type='REMOVE', quantity_recorded=10, unit_price=320, enterprise=enterprise_code)
        with pytest.raises(ValidationError) as ve:
            record2_recipe.make()
        msg = 'Please specify where to the items are being taken to from the inventory'
        assert msg in ve.value.messages
