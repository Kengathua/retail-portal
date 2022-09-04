import pytest
from django.test import TestCase
from django.core.exceptions import ValidationError

from elites_franchise_portal.franchises.models import Franchise
from elites_franchise_portal.items.models import (
    Brand, BrandItemType, Category, Item, ItemModel, ItemType,
    ItemUnits, UnitsItemType, Units)
from elites_franchise_portal.debit.models import (
    Inventory, InventoryItem, InventoryInventoryItem, InventoryRecord,
    Warehouse, WarehouseItem, WarehouseRecord)
from elites_franchise_portal.catalog.models import Catalog

from model_bakery import baker
from model_bakery.recipe import Recipe


class TestWarehouse(TestCase):

    def test_create_warehouse(self):
        franchise = baker.make(Franchise, name='Elites Age Supermarket')
        franchise_code = franchise.elites_code
        warehouse = baker.make(Warehouse, warehouse_name='Elites Private Warehouse', franchise=franchise_code)

        assert warehouse
        assert Warehouse.objects.count() == 1


class TestWarehouseItem(TestCase):

    def test_create_warehouse_item(self):
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
            franchise=franchise_code)
        warehouse = baker.make(
            Warehouse, warehouse_name='Elites Private Warehouse', franchise=franchise_code)
        warehouse_item = baker.make(WarehouseItem, item=item, franchise=franchise_code)
        warehouse_record = baker.make(
            WarehouseRecord, warehouse=warehouse, warehouse_item=warehouse_item,
            record_type='ADD', quantity_recorded=10, unit_price=300, franchise=franchise_code)

        assert warehouse
        assert warehouse_item
        assert Warehouse.objects.count() == 1
        assert WarehouseItem.objects.count() == 1
        assert warehouse_item.quantity == warehouse_record.closing_quantity == 10.0
        assert warehouse_item.total_amount == warehouse_record.closing_total_amount == 3000.0


class TestwarehouseRecord(TestCase):

    def test_add_to_warehouse_record(self):
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
            franchise=franchise_code)
        warehouse = baker.make(
            Warehouse, warehouse_name='Elites Private Warehouse', franchise=franchise_code)
        warehouse_item = baker.make(WarehouseItem, item=item, franchise=franchise_code)
        warehouse_record = baker.make(
            WarehouseRecord, warehouse=warehouse, warehouse_item=warehouse_item, record_type='ADD',
            quantity_recorded=10, unit_price=300, franchise=franchise_code)
        assert warehouse_record
        assert warehouse_record.total_amount_recorded == 3000.0
        assert warehouse_record.quantity_recorded == 10
        assert warehouse_record.closing_total_amount == 3000.0


    def test_remove_from_warehouse_record(self):
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
        warehouse = baker.make(
            Warehouse, warehouse_name='Elites Private Warehouse', franchise=franchise_code)
        item = baker.make(
            Item, item_model=item_model, barcode='83838388383', make_year=2020,
            franchise=franchise_code)
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
        master_inventory = baker.make(
            Inventory, inventory_name='Elites Age Supermarket Working Stock Inventory',
            is_master=True, is_active=True, inventory_type='WORKING STOCK',
            franchise=franchise_code)
        available_inventory = baker.make(
            Inventory, inventory_name='Elites Age Supermarket Available Inventory',
            is_active=True, inventory_type='AVAILABLE', franchise=franchise_code)
        inventory_item = baker.make(
            InventoryItem, item=item, franchise=franchise_code)
        baker.make(
            InventoryInventoryItem, inventory=master_inventory,
            inventory_item=inventory_item, franchise=franchise_code)
        baker.make(
            InventoryInventoryItem, inventory=available_inventory,
            inventory_item=inventory_item, franchise=franchise_code)
        warehouse = baker.make(
            Warehouse, warehouse_name='Elites Private Warehouse', franchise=franchise_code)
        warehouse_item = baker.make(WarehouseItem, item=item, franchise=franchise_code)
        record1 = baker.make(
            WarehouseRecord, warehouse=warehouse, warehouse_item=warehouse_item,
            record_type='ADD', quantity_recorded=15, unit_price=300, franchise=franchise_code)

        assert warehouse_item.quantity == record1.closing_quantity == 15.0
        assert warehouse_item.total_amount == record1.closing_total_amount == 4500.0

        record2 = baker.make(
            WarehouseRecord, warehouse=warehouse, warehouse_item=warehouse_item, record_type='REMOVE',
            removal_type = 'INVENTORY', quantity_recorded=10, unit_price=300, franchise=franchise_code)

        assert record2.opening_quantity == 15
        assert record2.opening_total_amount == 4500.0
        assert record2.total_amount_recorded == 3000.0
        assert record2.closing_total_amount == 1500.0
        assert warehouse_item.quantity == record2.closing_quantity == 5.0
        assert warehouse_item.total_amount == record2.closing_total_amount == 1500.0

    def test_fail_remove_from_warehouse_record_no_removal_type(self):
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
            franchise=franchise_code)
        warehouse = baker.make(
            Warehouse, warehouse_name='Elites Private Warehouse', franchise=franchise_code)
        warehouse_item = baker.make(WarehouseItem, item=item, franchise=franchise_code)
        baker.make(
            WarehouseRecord, warehouse=warehouse, warehouse_item=warehouse_item, record_type='ADD', quantity_recorded=15,
            unit_price=300, franchise=franchise_code)
        warehouse_record_recipe = Recipe(
            WarehouseRecord, warehouse=warehouse, warehouse_item=warehouse_item, quantity_recorded=10, record_type='REMOVE',
            unit_price=300, franchise=franchise_code)

        with pytest.raises(ValidationError) as ve:
            warehouse_record_recipe.make()
        msg = 'Please specify the removal type of this item from store'
        assert msg in ve.value.messages

    def test_fail_remove_from_empty_warehouse(self):
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
            franchise=franchise_code)
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
            Warehouse, warehouse_name='Elites Private Warehouse', franchise=franchise_code)
        warehouse_item = baker.make(WarehouseItem, item=item, franchise=franchise_code)
        warehouse_record_recipe = Recipe(
            WarehouseRecord, warehouse=warehouse, warehouse_item=warehouse_item, quantity_recorded=10,
            record_type='REMOVE', removal_type = 'INVENTORY', unit_price=300, franchise=franchise_code)

        with pytest.raises(ValidationError) as ve:
            warehouse_record_recipe.make()
        msg = 'The store is currently empty. Please add items to tranfer items from it'
        assert msg in ve.value.messages
