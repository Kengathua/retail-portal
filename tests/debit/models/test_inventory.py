"""."""

import pytest
from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError

from elites_retail_portal.enterprises.models import Enterprise
from elites_retail_portal.items.models import (
    Brand, BrandItemType, Category, Item, ItemModel, ItemType,
    ItemUnits, UnitsItemType, Units)
from elites_retail_portal.debit.models import (
    Inventory, InventoryItem, InventoryRecord, Sale)
from elites_retail_portal.warehouses.models import Warehouse
from elites_retail_portal.catalog.models import (
    CatalogItem, Section, Catalog, CatalogCatalogItem, CatalogItemAuditLog)
from elites_retail_portal.debit.models.inventory import InventoryInventoryItem
from elites_retail_portal.enterprise_mgt.models import (
    EnterpriseSetupRule, EnterpriseSetupRuleInventory,
    EnterpriseSetupRuleCatalog, EnterpriseSetupRuleWarehouse)

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

        assert str(inventory_item)
        assert not inventory_item.quantity
        assert not inventory_item.unit_price
        assert InventoryItem.objects.count() == 1

    def test_get_summary(self):
        """Test get summary."""
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
        inventory = baker.make(
            Inventory, inventory_name='Elites Age Supermarket AVAILABLE Inventory',
            is_master=True, is_default=True, is_active=True, inventory_type='AVAILABLE',
            enterprise=enterprise_code)
        catalog = baker.make(
            Catalog, catalog_name='Elites Age Supermarket Standard Catalog',
            description='Standard Catalog', is_standard=True, enterprise=enterprise_code)
        warehouse = baker.make(
            Warehouse, warehouse_name='Elites Private Warehouse', is_default=True,
            enterprise=enterprise_code)
        rule = baker.make(
            EnterpriseSetupRule, name='Elite Age Rules', is_default=True,
            is_active=True, enterprise=enterprise_code)
        baker.make(
            EnterpriseSetupRuleInventory, rule=rule, inventory=inventory,
            enterprise=enterprise_code)
        baker.make(
            EnterpriseSetupRuleWarehouse, rule=rule, warehouse=warehouse,
            enterprise=enterprise_code)
        baker.make(
            EnterpriseSetupRuleCatalog, rule=rule, catalog=catalog,
            enterprise=enterprise_code)
        inventory_item = baker.make(InventoryItem, item=item, enterprise=enterprise_code)
        baker.make(
            InventoryInventoryItem, inventory=inventory, inventory_item=inventory_item)
        record_date = timezone.now()
        record = baker.make(
            InventoryRecord, inventory=inventory, inventory_item=inventory_item,
            record_date=record_date, record_type='ADD', quantity_recorded=15,
            unit_price=300, enterprise=enterprise_code)

        assert record
        inventory.summary == [
            {
                'inventory_item': inventory_item,
                'quantity': 15.0,
                'total_amount': 4500.0
            }
        ]

        assert inventory_item.quantity == 15
        assert inventory_item.unit_price == 300
        assert inventory_item.total_amount == 4500

        # Update record
        record.quantity_recorded = 10
        record.unit_price = 310
        record.save()
        record.refresh_from_db()

        inventory.summary == [
            {
                'inventory_item': inventory_item,
                'quantity': 10.0,
                'total_amount': 4500
            }
        ]

        assert inventory_item.quantity == 10
        assert inventory_item.unit_price == 310
        assert inventory_item.total_amount == 4500


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
        baker.make(
            EnterpriseSetupRuleInventory, rule=rule, inventory=master_inventory,
            enterprise=enterprise_code)
        baker.make(
            EnterpriseSetupRuleInventory, rule=rule, inventory=available_inventory,
            enterprise=enterprise_code)
        baker.make(
            EnterpriseSetupRuleWarehouse, rule=rule, warehouse=warehouse,
            enterprise=enterprise_code)
        baker.make(
            EnterpriseSetupRuleCatalog, rule=rule, catalog=catalog,
            enterprise=enterprise_code)
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
        inventory_item.check_inventory_item_in_catalog_items(section)
        catalog_item = CatalogItem.objects.get(
            inventory_item=inventory_item, enterprise=inventory_item.enterprise)
        baker.make(
            CatalogCatalogItem, catalog=catalog, catalog_item=catalog_item,
            enterprise=enterprise_code)
        assert catalog_item.marked_price == 0
        assert catalog_item.quantity == 0

        assert CatalogItemAuditLog.objects.count() == 1

        record1 = baker.make(
            InventoryRecord, inventory=available_inventory, inventory_item=inventory_item,
            record_type='ADD', quantity_recorded=15, unit_price=300, enterprise=enterprise_code)
        catalog_item.refresh_from_db()
        assert CatalogItem.objects.count() == 1
        assert catalog_item.marked_price == record1.unit_price == 300
        assert catalog_item.quantity == record1.quantity_recorded == 15

        latest_audit = CatalogItemAuditLog.objects.filter().latest('audit_date')
        assert latest_audit.quantity_after == 15

        record2 = baker.make(
            InventoryRecord, inventory=available_inventory, inventory_item=inventory_item,
            record_type='ADD', quantity_recorded=15, unit_price=370, enterprise=enterprise_code)
        expected_total = record1.quantity_recorded + record2.quantity_recorded
        catalog_item.refresh_from_db()
        assert CatalogItem.objects.count() == 1
        assert catalog_item.marked_price == record2.unit_price == 370
        assert CatalogItemAuditLog.objects.count() == 3
        assert catalog_item.quantity == expected_total == 30

        latest_audit = CatalogItemAuditLog.objects.filter().latest('audit_date')
        assert latest_audit.quantity_after == expected_total == 30

        record1.save()
        record1.refresh_from_db()
        catalog_item.refresh_from_db()
        assert record1.closing_stock_quantity == 15
        assert CatalogItem.objects.count() == 1
        assert catalog_item.marked_price == record2.unit_price == 370
        assert catalog_item.quantity == expected_total == 30

        latest_audit = CatalogItemAuditLog.objects.filter().latest('audit_date')
        assert latest_audit.quantity_after == expected_total == 30

        record1.quantity_recorded = 10
        record1.unit_price = 330
        expected_total = expected_total - 5
        record1.save()

        record1.refresh_from_db()
        record2.refresh_from_db()
        assert record1.closing_stock_quantity == 10
        assert record2.closing_stock_quantity == 25
        catalog_item.refresh_from_db()
        assert CatalogItem.objects.count() == 1
        assert catalog_item.marked_price == record2.unit_price == 370
        assert catalog_item.quantity == expected_total == 25
        latest_audit = CatalogItemAuditLog.objects.filter().latest('audit_date')
        assert latest_audit.quantity_after == expected_total == 25

        record2.quantity_recorded = 18
        expected_total = expected_total + 3
        record2.unit_price = 400

        record2.save()

        assert CatalogItem.objects.count() == 1
        assert CatalogItemAuditLog.objects.count() == 5
        catalog_item.refresh_from_db()
        assert catalog_item.marked_price == record2.unit_price == 400
        assert catalog_item.quantity == expected_total == 28

        latest_audit = CatalogItemAuditLog.objects.filter().latest('audit_date')
        assert latest_audit.quantity_after == expected_total == 28

        record3 = baker.make(
            InventoryRecord, inventory=available_inventory, inventory_item=inventory_item,
            record_type='ADD', quantity_recorded=20, unit_price=320, enterprise=enterprise_code)
        expected_total = record1.quantity_recorded + record2.quantity_recorded + record3.quantity_recorded  # noqa
        catalog_item.refresh_from_db()
        assert CatalogItem.objects.count() == 1
        assert catalog_item.marked_price == record3.unit_price == 320
        assert catalog_item.quantity == expected_total == 48

        latest_audit = CatalogItemAuditLog.objects.filter().latest('audit_date')
        assert latest_audit.quantity_after == 48

        assert CatalogItemAuditLog.objects.count() == 6

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
        catalog = baker.make(
            Catalog, catalog_name='Elites Age Supermarket Standard Catalog',
            description='Standard Catalog', is_standard=True, enterprise=enterprise_code)
        warehouse = baker.make(
            Warehouse, warehouse_name='Elites Private Warehouse', is_default=True,
            enterprise=enterprise_code)
        rule = baker.make(
            EnterpriseSetupRule, name='Elite Age Rules', is_default=True,
            is_active=True, enterprise=enterprise_code)
        baker.make(
            EnterpriseSetupRuleInventory, rule=rule, inventory=master_inventory,
            enterprise=enterprise_code)
        baker.make(
            EnterpriseSetupRuleInventory, rule=rule, inventory=available_inventory,
            enterprise=enterprise_code)
        baker.make(
            EnterpriseSetupRuleWarehouse, rule=rule, warehouse=warehouse, enterprise=enterprise_code)
        baker.make(
            EnterpriseSetupRuleCatalog, rule=rule, catalog=catalog, enterprise=enterprise_code)
        inventory_item = baker.make(InventoryItem, item=item, enterprise=enterprise_code)
        baker.make(
            InventoryInventoryItem, inventory=master_inventory, inventory_item=inventory_item,
            enterprise=enterprise_code)
        baker.make(
            InventoryInventoryItem, inventory=available_inventory, inventory_item=inventory_item)
        section = baker.make(Section, section_name='Section A')
        baker.make(
            CatalogItem, section=section, inventory_item=inventory_item, enterprise=enterprise_code)
        record_recipe = Recipe(
            InventoryRecord, inventory=available_inventory, inventory_item=inventory_item,
            record_type='REMOVE', quantity_recorded=15, unit_price=300, enterprise=enterprise_code)

        with pytest.raises(ValidationError) as ve:
            record_recipe.make()
        msg = 'You are trying to remove 15.0 items of SAMSUNG GE731K-B SUT COOKER and '\
            'Elites Age Supermarket Available Inventory has 0.0 items'
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
        inventory = baker.make(
            Inventory, inventory_name='Elites Age Supermarket Available Inventory',
            is_default=True, is_master=True,
            is_active=True, inventory_type='AVAILABLE', enterprise=enterprise_code)
        catalog = baker.make(
            Catalog, catalog_name='Elites Age Supermarket Standard Catalog',
            is_default=True,
            description='Standard Catalog', is_standard=True, enterprise=enterprise_code)
        warehouse = baker.make(
            Warehouse, warehouse_name='Elites Private Warehouse', is_default=True,
            is_receiving=True, enterprise=enterprise_code)
        rule = baker.make(
            EnterpriseSetupRule, name='Elites Age', is_active=True, enterprise=enterprise_code)
        baker.make(
            EnterpriseSetupRuleInventory, rule=rule, inventory=inventory,
            enterprise=enterprise_code)
        baker.make(
            EnterpriseSetupRuleWarehouse, rule=rule, warehouse=warehouse,
            enterprise=enterprise_code)
        baker.make(
            EnterpriseSetupRuleCatalog, rule=rule, catalog=catalog,
            enterprise=enterprise_code)
        inventory_item = baker.make(InventoryItem, item=item, enterprise=enterprise_code)
        baker.make(
            InventoryInventoryItem, inventory=inventory, inventory_item=inventory_item)
        section = baker.make(Section, section_name='Section A')
        inventory_item.check_inventory_item_in_catalog_items(section)
        catalog_item = CatalogItem.objects.get(
            inventory_item=inventory_item, enterprise=enterprise_code)
        baker.make(
            CatalogCatalogItem, catalog=catalog, catalog_item=catalog_item,
            enterprise=enterprise_code)
        assert catalog_item.marked_price == 0
        assert catalog_item.quantity == 0

        record1 = baker.make(
            InventoryRecord, inventory=inventory, inventory_item=inventory_item,
            record_type='ADD', quantity_recorded=15, unit_price=300, enterprise=enterprise_code)
        catalog_item.refresh_from_db()
        assert CatalogItem.objects.count() == 1
        assert catalog_item.marked_price == record1.unit_price == 300
        assert catalog_item.quantity == record1.quantity_recorded == 15

        sale = baker.make(Sale, sale_code="S-001", enterprise=enterprise_code)
        record2 = baker.make(
            InventoryRecord, inventory=inventory, inventory_item=inventory_item,
            removal_guid=sale.id, record_type='REMOVE', removal_type='SALES',
            quantity_recorded=10, unit_price=320, enterprise=enterprise_code)
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
        inventory = baker.make(
            Inventory, inventory_name='Elites Age Supermarket Available Inventory',
            is_default=True, is_master=True,
            is_active=True, inventory_type='AVAILABLE', enterprise=enterprise_code)
        catalog = baker.make(
            Catalog, catalog_name='Elites Age Supermarket Standard Catalog',
            is_default=True,
            description='Standard Catalog', is_standard=True, enterprise=enterprise_code)
        warehouse = baker.make(
            Warehouse, warehouse_name='Elites Private Warehouse', is_default=True,
            is_receiving=True, enterprise=enterprise_code)
        rule = baker.make(
            EnterpriseSetupRule, name='Elites Age', is_active=True, enterprise=enterprise_code)
        baker.make(
            EnterpriseSetupRuleInventory, rule=rule, inventory=inventory,
            enterprise=enterprise_code)
        baker.make(
            EnterpriseSetupRuleWarehouse, rule=rule, warehouse=warehouse,
            enterprise=enterprise_code)
        baker.make(
            EnterpriseSetupRuleCatalog, rule=rule, catalog=catalog,
            enterprise=enterprise_code)
        inventory_item = baker.make(InventoryItem, item=item, enterprise=enterprise_code)
        baker.make(
            InventoryInventoryItem, inventory=inventory, inventory_item=inventory_item)
        section = baker.make(Section, section_name='Section A')
        inventory_item.check_inventory_item_in_catalog_items(section)
        catalog_item = CatalogItem.objects.get(
            inventory_item=inventory_item, enterprise=enterprise_code)
        baker.make(
            CatalogCatalogItem, catalog=catalog, catalog_item=catalog_item,
            enterprise=enterprise_code)
        assert catalog_item.marked_price == 0
        assert catalog_item.quantity == 0

        baker.make(
            InventoryRecord, inventory=inventory, inventory_item=inventory_item,
            record_type='ADD', quantity_recorded=15, unit_price=300, enterprise=enterprise_code)

        record2_recipe = Recipe(
            InventoryRecord, inventory=inventory, inventory_item=inventory_item,
            record_type='REMOVE', quantity_recorded=10, unit_price=320, enterprise=enterprise_code)
        with pytest.raises(ValidationError) as ve:
            record2_recipe.make()
        msg = 'Please specify where to the items are being taken to from the inventory'
        assert msg in ve.value.messages


    def test_update_catalog_item_new_records(self):
        """Update catalog item."""
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
        inventory = baker.make(
            Inventory, inventory_name='Elites Age Supermarket AVAILABLE Inventory',
            is_master=True, is_default=True, is_active=True, inventory_type='AVAILABLE',
            enterprise=enterprise_code)
        catalog = baker.make(
            Catalog, catalog_name='Elites Age Supermarket Standard Catalog',
            description='Standard Catalog', is_standard=True, enterprise=enterprise_code)
        warehouse = baker.make(
            Warehouse, warehouse_name='Elites Private Warehouse', is_default=True,
            enterprise=enterprise_code)
        rule = baker.make(
            EnterpriseSetupRule, name='Elite Age Rules', is_default=True,
            is_active=True, enterprise=enterprise_code)
        baker.make(
            EnterpriseSetupRuleInventory, rule=rule, inventory=inventory,
            enterprise=enterprise_code)
        baker.make(
            EnterpriseSetupRuleWarehouse, rule=rule, warehouse=warehouse,
            enterprise=enterprise_code)
        baker.make(
            EnterpriseSetupRuleCatalog, rule=rule, catalog=catalog,
            enterprise=enterprise_code)
        inventory_item = baker.make(InventoryItem, item=item, enterprise=enterprise_code)
        baker.make(
            InventoryInventoryItem, inventory=inventory, inventory_item=inventory_item)
        record_date = timezone.now()
        record1 = baker.make(
            InventoryRecord, inventory=inventory, inventory_item=inventory_item,
            record_date=record_date, record_type='ADD', quantity_recorded=15,
            unit_price=300, enterprise=enterprise_code)

        assert record1
        assert not CatalogItem.objects.filter(inventory_item=inventory_item).count()
        assert not CatalogItemAuditLog.objects.count()

        section = baker.make(Section, section_name='Section A')
        inventory_item.check_inventory_item_in_catalog_items(section)
        catalog_item = CatalogItem.objects.get(
            inventory_item=inventory_item, enterprise=enterprise_code)

        assert catalog_item.quantity == 15
        assert CatalogItemAuditLog.objects.count() == 1
        audit_log1 = CatalogItemAuditLog.objects.first()
        assert audit_log1.audit_source == 'CATALOG ITEM'
        assert audit_log1.catalog_item == catalog_item
        assert audit_log1.record_type == 'ADD'
        assert audit_log1.operation_type == 'CREATE CATALOG ITEM'
        assert audit_log1.quantity_before == 0
        assert audit_log1.quantity_recorded == 15
        assert audit_log1.quantity_after == 15
        assert audit_log1.selling_price_recorded == 300
        assert audit_log1.selling_price_after == 300
        assert audit_log1.threshold_price_recorded == 300
        assert audit_log1.threshold_price_after == 300
        assert audit_log1.discount_amount_recorded == 0
        assert audit_log1.discount_amount_after == 0

        sale = baker.make(Sale, sale_code="S-001", enterprise=enterprise_code)
        record2 = baker.make(
            InventoryRecord, inventory=inventory, inventory_item=inventory_item,
            record_date=record_date, record_type='REMOVE', removal_type='SALES',
            quantity_recorded=3, removal_guid=sale.id,
            unit_price=320, enterprise=enterprise_code)
        assert record2
        assert CatalogItemAuditLog.objects.count() == 2

        audit_log2 = CatalogItemAuditLog.objects.latest('audit_date')
        assert audit_log2.audit_source == 'INVENTORY RECORD'
        assert audit_log2.catalog_item == catalog_item
        assert audit_log2.record_type == 'REMOVE'
        assert audit_log2.operation_type == 'CREATE INVENTORY RECORD'
        assert audit_log2.quantity_before == 15
        assert audit_log2.quantity_recorded == -3
        assert audit_log2.quantity_after == 12
        assert audit_log2.selling_price_recorded == 300
        assert audit_log2.selling_price_after == 300
        assert audit_log2.threshold_price_recorded == 300
        assert audit_log2.threshold_price_after == 300
        assert audit_log2.discount_amount_recorded == 0
        assert audit_log2.discount_amount_after == 0

        allocated_inventory = baker.make(
            Inventory, inventory_name='Elites Age Supermarket Working Stock Inventory',
            inventory_type='ALLOCATED', enterprise=enterprise_code)
        baker.make(
            InventoryInventoryItem, inventory=allocated_inventory, inventory_item=inventory_item)

        # This should not affect the catalog item
        record3 = baker.make(
            InventoryRecord, inventory=allocated_inventory, inventory_item=inventory_item,
            record_date=record_date, record_type='ADD', quantity_recorded=3,
            unit_price=320, enterprise=enterprise_code)
        assert record3
        assert CatalogItemAuditLog.objects.count() == 2

    def test_update_catalog_item_update_records(self):
        """Update catalog item."""
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
        inventory = baker.make(
            Inventory, inventory_name='Elites Age Supermarket AVAILABLE Inventory',
            is_master=True, is_default=True, is_active=True, inventory_type='AVAILABLE',
            enterprise=enterprise_code)
        catalog = baker.make(
            Catalog, catalog_name='Elites Age Supermarket Standard Catalog',
            description='Standard Catalog', is_standard=True, enterprise=enterprise_code)
        warehouse = baker.make(
            Warehouse, warehouse_name='Elites Private Warehouse', is_default=True,
            enterprise=enterprise_code)
        rule = baker.make(
            EnterpriseSetupRule, name='Elite Age Rules', is_default=True,
            is_active=True, enterprise=enterprise_code)
        baker.make(
            EnterpriseSetupRuleInventory, rule=rule, inventory=inventory,
            enterprise=enterprise_code)
        baker.make(
            EnterpriseSetupRuleWarehouse, rule=rule, warehouse=warehouse,
            enterprise=enterprise_code)
        baker.make(
            EnterpriseSetupRuleCatalog, rule=rule, catalog=catalog,
            enterprise=enterprise_code)
        inventory_item = baker.make(InventoryItem, item=item, enterprise=enterprise_code)
        baker.make(
            InventoryInventoryItem, inventory=inventory, inventory_item=inventory_item)
        record_date1 = timezone.now()
        record1 = baker.make(
            InventoryRecord, inventory=inventory, inventory_item=inventory_item,
            record_date=record_date1, record_type='ADD', quantity_recorded=15,
            unit_price=300, enterprise=enterprise_code)

        assert record1
        assert not CatalogItem.objects.filter(inventory_item=inventory_item).count()
        assert not CatalogItemAuditLog.objects.count()

        section = baker.make(Section, section_name='Section A')
        catalog_item = baker.make(
            CatalogItem, section=section, inventory_item=inventory_item, discount_amount=20,
            enterprise=enterprise_code)

        assert catalog_item.quantity == 15
        assert catalog_item.marked_price == 300
        assert catalog_item.discount_amount == 20
        assert catalog_item.selling_price == 280
        assert catalog_item.threshold_price == 280

        assert CatalogItemAuditLog.objects.count() == 1
        audit_log1 = CatalogItemAuditLog.objects.first()
        assert audit_log1.audit_source == 'CATALOG ITEM'
        assert audit_log1.catalog_item == catalog_item
        assert audit_log1.record_type == 'ADD'
        assert audit_log1.operation_type == 'CREATE CATALOG ITEM'
        assert audit_log1.quantity_before == 0
        assert audit_log1.quantity_recorded == 15
        assert audit_log1.quantity_after == 15
        assert audit_log1.selling_price_before == 0
        assert audit_log1.selling_price_recorded == 280
        assert audit_log1.selling_price_after == 280
        assert audit_log1.threshold_price_before == 0
        assert audit_log1.threshold_price_recorded == 280
        assert audit_log1.threshold_price_after == 280
        assert audit_log1.discount_amount_before == 0
        assert audit_log1.discount_amount_recorded == 20
        assert audit_log1.discount_amount_after == 20

        # update the inventory record
        record1.quantity_recorded = 18
        record1.unit_price = 280
        record1.save()
        assert CatalogItemAuditLog.objects.count() == 2
        audit_log2 = CatalogItemAuditLog.objects.latest('audit_date')

        catalog_item.refresh_from_db()
        assert catalog_item.quantity == 18
        assert catalog_item.marked_price == 280
        assert catalog_item.discount_amount == 20
        assert catalog_item.selling_price == 260
        assert catalog_item.threshold_price == 260

        assert audit_log2.audit_source == 'INVENTORY RECORD'
        assert audit_log2.inventory_record == record1
        assert audit_log2.catalog_item == catalog_item
        assert audit_log2.record_type == 'ADD'
        assert audit_log2.operation_type == 'CREATE INVENTORY RECORD'
        assert audit_log2.audit_type == 'CREATE'
        assert audit_log2.quantity_before == 15
        assert audit_log2.quantity_recorded == 3
        assert audit_log2.quantity_after == 18
        assert audit_log2.selling_price_before == 280
        assert audit_log2.selling_price_recorded == 260
        assert audit_log2.selling_price_after == 260
        assert audit_log2.threshold_price_before == 280
        assert audit_log2.threshold_price_recorded == 260
        assert audit_log2.threshold_price_after == 260
        assert audit_log2.discount_amount_before == 20
        assert audit_log2.discount_amount_recorded == 20
        assert audit_log2.discount_amount_after == 20

        # update the record again -> It now has an audit log attached to it
        record1.quantity_recorded = 14
        record1.unit_price = 340
        record1.save()
        assert CatalogItemAuditLog.objects.count() == 3
        audit_log3 = CatalogItemAuditLog.objects.latest('audit_date')

        catalog_item.refresh_from_db()
        assert catalog_item.quantity == 14
        assert catalog_item.marked_price == 340
        assert catalog_item.discount_amount == 20
        assert catalog_item.selling_price == 320
        assert catalog_item.threshold_price == 260

        assert audit_log3.audit_source == 'INVENTORY RECORD'
        assert audit_log3.inventory_record == record1
        assert audit_log3.catalog_item == catalog_item
        assert audit_log3.record_type == 'ADD'
        assert audit_log3.operation_type == 'UPDATE INVENTORY RECORD'
        assert audit_log3.audit_type == 'UPDATE'
        assert audit_log3.quantity_before == 18
        assert audit_log3.quantity_recorded == -4
        assert audit_log3.quantity_after == 14
        assert audit_log3.selling_price_before == 260
        assert audit_log3.selling_price_recorded == 320
        assert audit_log3.selling_price_after == 320
        assert audit_log3.threshold_price_before == 260
        assert audit_log3.threshold_price_recorded == 260
        assert audit_log3.threshold_price_after == 260
        assert audit_log3.discount_amount_before == 20
        assert audit_log3.discount_amount_recorded == 20
        assert audit_log3.discount_amount_after == 20

        # CLEAN REMOVE

        sale = baker.make(Sale, sale_code="S-001", enterprise=enterprise_code)
        record_date2 = timezone.now()
        record2 = baker.make(
            InventoryRecord, inventory=inventory, inventory_item=inventory_item,
            record_date=record_date2, record_type='REMOVE', removal_type='SALES',
            quantity_recorded=3, removal_guid=sale.id,
            unit_price=320, enterprise=enterprise_code)
        assert record2
        assert CatalogItemAuditLog.objects.count() == 4

        catalog_item.refresh_from_db()
        assert catalog_item.quantity == 11
        assert catalog_item.marked_price == 340
        assert catalog_item.discount_amount == 20
        assert catalog_item.selling_price == 320
        assert catalog_item.threshold_price == 260

        audit_log4 = CatalogItemAuditLog.objects.latest('audit_date')
        assert audit_log4.audit_source == 'INVENTORY RECORD'
        assert audit_log4.catalog_item == catalog_item
        assert audit_log4.record_type == 'REMOVE'
        assert audit_log4.operation_type == 'CREATE INVENTORY RECORD'
        assert audit_log4.quantity_before == 14
        assert audit_log4.quantity_recorded == -3
        assert audit_log4.quantity_after == 11
        assert audit_log4.selling_price_before == 320
        assert audit_log4.selling_price_recorded == 320
        assert audit_log4.selling_price_after == 320
        assert audit_log4.threshold_price_before == 260
        assert audit_log4.threshold_price_recorded == 260
        assert audit_log4.threshold_price_after == 260
        assert audit_log4.discount_amount_before == 20
        assert audit_log4.discount_amount_recorded == 20
        assert audit_log4.discount_amount_after == 20

        allocated_inventory = baker.make(
            Inventory, inventory_name='Elites Age Supermarket Working Stock Inventory',
            inventory_type='ALLOCATED', enterprise=enterprise_code)
        baker.make(
            InventoryInventoryItem, inventory=allocated_inventory,
            inventory_item=inventory_item)

        # This should not affect the catalog item
        record_date3 = timezone.now()
        record3 = baker.make(
            InventoryRecord, inventory=allocated_inventory, inventory_item=inventory_item,
            record_date=record_date3, record_type='ADD', quantity_recorded=3,
            unit_price=320, enterprise=enterprise_code)
        assert record3
        assert CatalogItemAuditLog.objects.count() == 4

        # Update removal record
        record2.quantity_recorded = 4
        record2.unit_price = 330
        record2.save()

        catalog_item.refresh_from_db()
        assert catalog_item.quantity == 10
        assert catalog_item.marked_price == 340
        assert catalog_item.discount_amount == 20
        assert catalog_item.selling_price == 320
        assert catalog_item.threshold_price == 260

        audit_log4 = CatalogItemAuditLog.objects.latest('audit_date')
        assert audit_log4.audit_source == 'INVENTORY RECORD'
        assert audit_log4.catalog_item == catalog_item
        assert audit_log4.record_type == 'REMOVE'
        assert audit_log4.operation_type == 'CREATE INVENTORY RECORD'
        assert audit_log4.quantity_before == 11
        assert audit_log4.quantity_recorded == -1
        assert audit_log4.quantity_after == 10
        assert audit_log4.selling_price_before == 320
        assert audit_log4.selling_price_recorded == 320
        assert audit_log4.selling_price_after == 320
        assert audit_log4.threshold_price_before == 260
        assert audit_log4.threshold_price_recorded == 260
        assert audit_log4.threshold_price_after == 260
        assert audit_log4.discount_amount_before == 20
        assert audit_log4.discount_amount_recorded == 20
        assert audit_log4.discount_amount_after == 20

    def test_update_catalog_item_update_records_catalog_item_added_first(self):
        """Update catalog item."""
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
        inventory = baker.make(
            Inventory, inventory_name='Elites Age Supermarket AVAILABLE Inventory',
            is_master=True, is_default=True, is_active=True, inventory_type='AVAILABLE',
            enterprise=enterprise_code)
        catalog = baker.make(
            Catalog, catalog_name='Elites Age Supermarket Standard Catalog',
            description='Standard Catalog', is_standard=True, enterprise=enterprise_code)
        warehouse = baker.make(
            Warehouse, warehouse_name='Elites Private Warehouse', is_default=True,
            enterprise=enterprise_code)
        rule = baker.make(
            EnterpriseSetupRule, name='Elite Age Rules', is_default=True,
            is_active=True, enterprise=enterprise_code)
        baker.make(
            EnterpriseSetupRuleInventory, rule=rule, inventory=inventory,
            enterprise=enterprise_code)
        baker.make(
            EnterpriseSetupRuleWarehouse, rule=rule, warehouse=warehouse,
            enterprise=enterprise_code)
        baker.make(
            EnterpriseSetupRuleCatalog, rule=rule, catalog=catalog,
            enterprise=enterprise_code)
        inventory_item = baker.make(InventoryItem, item=item, enterprise=enterprise_code)
        baker.make(
            InventoryInventoryItem, inventory=inventory, inventory_item=inventory_item)
        section = baker.make(Section, section_name='Section A')
        catalog_item = baker.make(
            CatalogItem, section=section, inventory_item=inventory_item,
            enterprise=enterprise_code)

        assert catalog_item
        assert CatalogItemAuditLog.objects.count() == 1

        record_date = timezone.now()
        record = baker.make(
            InventoryRecord, inventory=inventory, inventory_item=inventory_item,
            record_date=record_date, record_type='ADD', quantity_recorded=15,
            unit_price=300, enterprise=enterprise_code)

        assert record
        assert CatalogItem.objects.filter(inventory_item=inventory_item).count() == 1
        assert CatalogItemAuditLog.objects.count() == 2

        catalog_item.refresh_from_db()
        assert catalog_item.quantity == 15
        assert catalog_item.marked_price == 300
        assert catalog_item.discount_amount == 0
        assert catalog_item.selling_price == 300
        assert catalog_item.threshold_price == 300

        audit_log1 = CatalogItemAuditLog.objects.filter(inventory_record=record).first()

        assert audit_log1.audit_source == 'INVENTORY RECORD'
        assert audit_log1.catalog_item == catalog_item
        assert audit_log1.record_type == 'ADD'
        assert audit_log1.operation_type == 'CREATE INVENTORY RECORD'
        assert audit_log1.quantity_before == 0
        assert audit_log1.quantity_recorded == 15
        assert audit_log1.quantity_after == 15
        assert audit_log1.selling_price_before == 0
        assert audit_log1.selling_price_recorded == 300
        assert audit_log1.selling_price_after == 300
        assert audit_log1.threshold_price_before == 0
        assert audit_log1.threshold_price_recorded == 300
        assert audit_log1.threshold_price_after == 300
        assert audit_log1.discount_amount_before == 0
        assert audit_log1.discount_amount_recorded == 0
        assert audit_log1.discount_amount_after == 0