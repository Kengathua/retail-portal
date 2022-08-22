import pytest
from django.test import TestCase
from django.core.exceptions import ValidationError

from elites_franchise_portal.franchises.models import Franchise
from elites_franchise_portal.items.models import (
    Brand, BrandItemType, Category, Item, ItemModel, ItemType,
    ItemUnits, UnitsItemType, Units)
from elites_franchise_portal.debit.models import (
    Warehouse, WarehouseItem, WarehouseRecord,
    Inventory, InventoryItem, InventoryRecord)
from elites_franchise_portal.catalog.models import CatalogItem, Section

from model_bakery import baker
from model_bakery.recipe import Recipe


class TestInventory(TestCase):
    """."""

    def test_create_inventory(self):
        """."""
        franchise = baker.make(Franchise, name='Elites Age Supermarket')
        franchise_code = franchise.elites_code
        inventory = baker.make(
            Inventory, inventory_name='Elites Age Supermarket Working Stock Inventory',
            inventory_type='WORKING STOCK', franchise=franchise_code)

        assert inventory
        assert Inventory.objects.count() == 1

class TestInventoryItem(TestCase):
    """."""

    def test_create_inventory_item(self):
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
        item_model = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731K-B SUT',
            franchise=franchise_code)
        item = baker.make(
            Item, item_model=item_model, barcode='83838388383', make_year=2020,
            franchise=franchise_code, create_inventory_item=False)
        inventory_item = baker.make(InventoryItem, item=item, franchise=franchise_code)

        assert inventory_item
        assert InventoryItem.objects.count() == 1

    def test_catalog_created_after_inventory_item(self):
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
        item_model = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731K-B SUT',
            franchise=franchise_code)
        item = baker.make(
            Item, item_model=item_model, barcode='83838388383', make_year=2020,
            franchise=franchise_code, create_inventory_item=False)
        s_units = baker.make(Units, units_name='packet', franchise=franchise_code)
        baker.make(UnitsItemType, item_type=item_type, units=s_units, franchise=franchise_code)
        s_units.item_types.set([item_type])
        s_units.save()
        p_units = baker.make(Units, units_name='Dozen', franchise=franchise_code)
        baker.make(UnitsItemType, item_type=item_type, units=p_units, franchise=franchise_code)
        p_units.item_types.set([item_type])
        p_units.save()
        baker.make(
            ItemUnits, item=item, sales_units=s_units, purchases_units=p_units,
            items_per_purchase_unit=12, franchise=franchise_code)
        warehouse = baker.make(
            Warehouse, warehouse_name='Elites Franchise Private Warehouse',
            warehouse_type='PRIVATE', franchise=franchise_code)
        warehouseitem = baker.make(WarehouseItem, item=item, franchise=franchise_code)
        baker.make(
            WarehouseRecord, warehouse=warehouse, warehouse_item=warehouseitem, record_type='ADD', quantity_recorded=10,
            unit_price=300, franchise=franchise_code)
        inventory_item = baker.make(
            InventoryItem, item=item, franchise=franchise_code)
        section = baker.make(Section, section_name='Section A')
        inventory_item.check_item_in_catalog_items(section)
        catalog_item = CatalogItem.objects.get(inventory_item=inventory_item, franchise=inventory_item.franchise)
        assert catalog_item


class TestInventoryRecord(TestCase):

    def test_create_inventory_record(self):
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
        item_model = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731K-B SUT',
            franchise=franchise_code)
        item = baker.make(
            Item, item_model=item_model, barcode='83838388383', make_year=2020,
            franchise=franchise_code, create_inventory_item=False)
        s_units = baker.make(Units, units_name='packet', franchise=franchise_code)
        baker.make(UnitsItemType, item_type=item_type, units=s_units, franchise=franchise_code)
        s_units.item_types.set([item_type])
        s_units.save()
        p_units = baker.make(Units, units_name='Dozen', franchise=franchise_code)
        baker.make(UnitsItemType, item_type=item_type, units=p_units, franchise=franchise_code)
        p_units.item_types.set([item_type])
        p_units.save()
        baker.make(
            ItemUnits, item=item, sales_units=s_units, purchases_units=p_units,
            items_per_purchase_unit=12, franchise=franchise_code)
        inventory_item = baker.make(InventoryItem, item=item, franchise=franchise_code)
        record = baker.make(
            InventoryRecord, inventory_item=inventory_item, record_type='ADD',
            quantity_recorded=15, unit_price=300, franchise=franchise_code)

        assert record
        assert record.opening_stock_quantity == 0.0
        assert record.opening_stock_total_amount == 0.0
        assert record.closing_stock_quantity == 15.0
        assert record.total_amount_recorded == 4500.0
        assert record.closing_stock_total_amount == 4500.0
        assert InventoryRecord.objects.count() == 1

    def test_add_item_to_inventory_multiple_items(self):
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
        item_model = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731K-B SUT',
            franchise=franchise_code)
        item = baker.make(
            Item, item_model=item_model, barcode='83838388383', make_year=2020,
            franchise=franchise_code, create_inventory_item=False)
        s_units = baker.make(Units, units_name='packet', franchise=franchise_code)
        baker.make(UnitsItemType, item_type=item_type, units=s_units, franchise=franchise_code)
        s_units.item_types.set([item_type])
        s_units.save()
        p_units = baker.make(Units, units_name='Dozen', franchise=franchise_code)
        baker.make(UnitsItemType, item_type=item_type, units=p_units, franchise=franchise_code)
        p_units.item_types.set([item_type])
        p_units.save()
        baker.make(
            ItemUnits, item=item, sales_units=s_units, purchases_units=p_units,
            items_per_purchase_unit=12, franchise=franchise_code)
        inventory_item = baker.make(InventoryItem, item=item, franchise=franchise_code)
        record1 = baker.make(
            InventoryRecord, inventory_item=inventory_item, record_type='ADD',
            quantity_recorded=15, unit_price=300, franchise=franchise_code)
        record2 = baker.make(
            InventoryRecord, inventory_item=inventory_item, record_type='ADD',
            quantity_recorded=10, unit_price=300, franchise=franchise_code)

        assert record1
        assert record1.opening_stock_quantity == 0.0
        assert record1.opening_stock_total_amount == 0.0
        assert record1.closing_stock_quantity == 15.0
        assert record1.total_amount_recorded == 4500.0
        assert record1.closing_stock_total_amount == 4500.0

        assert record2
        assert record2.opening_stock_quantity == 15.0
        assert record2.opening_stock_total_amount == 4500.0
        assert record2.closing_stock_quantity == 25.0
        assert record2.total_amount_recorded == 3000.0
        assert record2.closing_stock_total_amount == 7500.0

    def test_update_catalog_after_adding_inventory_record(self):
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
        item_model = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731K-B SUT',
            franchise=franchise_code)
        item = baker.make(
            Item, item_model=item_model, barcode='83838388383', make_year=2020,
            franchise=franchise_code, create_inventory_item=False)
        s_units = baker.make(Units, units_name='packet', franchise=franchise_code)
        baker.make(UnitsItemType, item_type=item_type, units=s_units, franchise=franchise_code)
        s_units.item_types.set([item_type])
        s_units.save()
        p_units = baker.make(Units, units_name='Dozen', franchise=franchise_code)
        baker.make(UnitsItemType, item_type=item_type, units=p_units, franchise=franchise_code)
        p_units.item_types.set([item_type])
        p_units.save()
        baker.make(
            ItemUnits, item=item, sales_units=s_units, purchases_units=p_units,
            items_per_purchase_unit=12, franchise=franchise_code)
        inventory_item = baker.make(InventoryItem, item=item, franchise=franchise_code)
        section = baker.make(Section, section_name='Section A')
        inventory_item.check_item_in_catalog_items(section)
        catalog_item = CatalogItem.objects.get(
            inventory_item=inventory_item, franchise=inventory_item.franchise)
        assert catalog_item.marked_price == 0
        assert catalog_item.quantity == 0

        record1 = baker.make(
            InventoryRecord, inventory_item=inventory_item, record_type='ADD',
            quantity_recorded=15, unit_price=300, franchise=franchise_code)
        catalog_item.refresh_from_db()
        assert CatalogItem.objects.count() == 1
        assert catalog_item.marked_price == record1.unit_price == 300
        assert catalog_item.quantity == record1.quantity_recorded == 15


        record2 = baker.make(
            InventoryRecord, inventory_item=inventory_item, record_type='ADD',
            quantity_recorded=15, unit_price=370, franchise=franchise_code)
        expected_total = record1.quantity_recorded + record2.quantity_recorded
        catalog_item.refresh_from_db()
        assert CatalogItem.objects.count() == 1
        assert catalog_item.marked_price == record2.unit_price == 370
        assert catalog_item.quantity == expected_total == 30

        record3 = baker.make(
            InventoryRecord, inventory_item=inventory_item, record_type='ADD',
            quantity_recorded=20, unit_price=320, franchise=franchise_code)
        expected_total = record1.quantity_recorded + record2.quantity_recorded + record3.quantity_recorded
        catalog_item.refresh_from_db()
        assert CatalogItem.objects.count() == 1
        assert catalog_item.marked_price == record3.unit_price == 320
        assert catalog_item.quantity == expected_total == 50


    def test_fail_remove_from_empty_inventory(self):
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
        item_model = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731K-B SUT',
            franchise=franchise_code)
        item = baker.make(
            Item, item_model=item_model, barcode='83838388383', make_year=2020,
            franchise=franchise_code, create_inventory_item=False)
        s_units = baker.make(Units, units_name='packet', franchise=franchise_code)
        baker.make(UnitsItemType, item_type=item_type, units=s_units, franchise=franchise_code)
        s_units.item_types.set([item_type])
        s_units.save()
        p_units = baker.make(Units, units_name='Dozen', franchise=franchise_code)
        baker.make(UnitsItemType, item_type=item_type, units=p_units, franchise=franchise_code)
        p_units.item_types.set([item_type])
        p_units.save()
        baker.make(
            ItemUnits, item=item, sales_units=s_units, purchases_units=p_units,
            items_per_purchase_unit=12, franchise=franchise_code)
        inventory_item = baker.make(InventoryItem, item=item, franchise=franchise_code)
        record_recipe = Recipe(
            InventoryRecord, inventory_item=inventory_item, record_type='REMOVE',
            quantity_recorded=15, unit_price=300, franchise=franchise_code)

        with pytest.raises(ValidationError) as ve:
            record_recipe.make()
        msg = 'You are trying to remove 15.0 items and the inventory has 0 items'
        assert msg in ve.value.messages

    def test_remove_from_inventory(self):
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
        item_model = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731K-B SUT',
            franchise=franchise_code)
        item = baker.make(
            Item, item_model=item_model, barcode='83838388383', make_year=2020,
            franchise=franchise_code, create_inventory_item=False)
        s_units = baker.make(Units, units_name='packet', franchise=franchise_code)
        baker.make(UnitsItemType, item_type=item_type, units=s_units, franchise=franchise_code)
        s_units.item_types.set([item_type])
        s_units.save()
        p_units = baker.make(Units, units_name='Dozen', franchise=franchise_code)
        baker.make(UnitsItemType, item_type=item_type, units=p_units, franchise=franchise_code)
        p_units.item_types.set([item_type])
        p_units.save()
        baker.make(
            ItemUnits, item=item, sales_units=s_units, purchases_units=p_units,
            items_per_purchase_unit=12, franchise=franchise_code)
        inventory_item = baker.make(InventoryItem, item=item, franchise=franchise_code)
        section = baker.make(Section, section_name='Section A')
        inventory_item.check_item_in_catalog_items(section)
        catalog_item = CatalogItem.objects.get(
            inventory_item=inventory_item, franchise=inventory_item.franchise)
        assert catalog_item.marked_price == 0
        assert catalog_item.quantity == 0

        record1 = baker.make(
            InventoryRecord, inventory_item=inventory_item, record_type='ADD',
            quantity_recorded=15, unit_price=300, franchise=franchise_code)
        catalog_item.refresh_from_db()
        assert CatalogItem.objects.count() == 1
        assert catalog_item.marked_price == record1.unit_price == 300
        assert catalog_item.quantity == record1.quantity_recorded == 15

        record2 = baker.make(
            InventoryRecord, inventory_item=inventory_item, record_type='REMOVE',
            removal_type = 'SALES',
            quantity_recorded=10, unit_price=320, franchise=franchise_code)
        expected_total = record1.quantity_recorded - record2.quantity_recorded
        catalog_item.refresh_from_db()
        assert catalog_item.marked_price == record1.unit_price == 300
        assert catalog_item.quantity == expected_total == 5


    def test_fail_remove_items_from_inventory_missing_removal_type(self):
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
        item_model = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731K-B SUT',
            franchise=franchise_code)
        item = baker.make(
            Item, item_model=item_model, barcode='83838388383', make_year=2020,
            franchise=franchise_code, create_inventory_item=False)
        s_units = baker.make(Units, units_name='packet', franchise=franchise_code)
        baker.make(UnitsItemType, item_type=item_type, units=s_units, franchise=franchise_code)
        s_units.item_types.set([item_type])
        s_units.save()
        p_units = baker.make(Units, units_name='Dozen', franchise=franchise_code)
        baker.make(UnitsItemType, item_type=item_type, units=p_units, franchise=franchise_code)
        p_units.item_types.set([item_type])
        p_units.save()
        baker.make(
            ItemUnits, item=item, sales_units=s_units, purchases_units=p_units,
            items_per_purchase_unit=12, franchise=franchise_code)
        inventory_item = baker.make(InventoryItem, item=item, franchise=franchise_code)
        section = baker.make(Section, section_name='Section A')
        inventory_item.check_item_in_catalog_items(section)
        catalog_item = CatalogItem.objects.get(
            inventory_item=inventory_item, franchise=inventory_item.franchise)
        assert catalog_item.marked_price == 0
        assert catalog_item.quantity == 0

        baker.make(
            InventoryRecord, inventory_item=inventory_item, record_type='ADD',
            quantity_recorded=15, unit_price=300, franchise=franchise_code)

        record2_recipe = Recipe(
            InventoryRecord, inventory_item=inventory_item, record_type='REMOVE',
            quantity_recorded=10, unit_price=320, franchise=franchise_code)
        with pytest.raises(ValidationError) as ve:
            record2_recipe.make()
        msg = 'Please specify where to the items are being taken to from the inventory'
        assert msg in ve.value.messages
