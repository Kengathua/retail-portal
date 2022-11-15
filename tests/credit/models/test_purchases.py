from django.test import TestCase

from elites_franchise_portal.enterprises.models import Enterprise
from elites_franchise_portal.items.models import (
    Brand, BrandItemType, Category, Item, ItemModel, ItemType,
    ItemUnits, UnitsItemType, Units)
from elites_franchise_portal.debit.models import (
    InventoryRecord, Inventory, InventoryInventoryItem, InventoryItem)
from elites_franchise_portal.warehouses.models import (
    WarehouseRecord, Warehouse, WarehouseItem)
from elites_franchise_portal.enterprise_mgt.models import EnterpriseSetupRules
from elites_franchise_portal.catalog.models import Catalog
from elites_franchise_portal.credit.models import Purchase, PurchaseItem

from model_bakery import baker


class TestPurchase(TestCase):
    """."""

    def test_create_purchase_record(self):
        """."""
        franchise = baker.make(
            Enterprise, name='Enterprise One', enterprise_code='EAL-E/EO-MB/2201-01',
            business_type='SHOP')
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
            EnterpriseSetupRules, master_inventory=master_inventory,
            default_inventory=available_inventory, receiving_warehouse=receiving_warehouse,
            default_warehouse=receiving_warehouse, standard_catalog=catalog,
            default_catalog=catalog, is_active=True, enterprise=enterprise_code)
        inventory_item = baker.make(InventoryItem, item=item, enterprise=enterprise_code)
        baker.make(
            InventoryInventoryItem, inventory=master_inventory, inventory_item=inventory_item)
        baker.make(
            InventoryInventoryItem, inventory=available_inventory, inventory_item=inventory_item)
        supplier = baker.make(Enterprise, name='LG Supplier')
        purchase = baker.make(
            Purchase, invoice_number='INV-001', supplier=supplier, enterprise=enterprise_code)
        purchase_item = baker.make(
            PurchaseItem,purchase=purchase, item=item, quantity_purchased=10, total_price=10000,
            recommended_retail_price=100, quantity_to_inventory=40,
            quantity_to_inventory_on_display=10, quantity_to_inventory_in_warehouse=30,
            enterprise=enterprise_code)

        purchase_item.refresh_from_db()
        assert float(purchase_item.unit_price) == 83.34

        assert Warehouse.objects.count() == 1
        assert WarehouseRecord.objects.count() == 2
        assert InventoryRecord.objects.count() == 1

        warehouse_record1 = WarehouseRecord.objects.get(
            warehouse_item__item=purchase_item.item, record_type='ADD')
        assert warehouse_record1.opening_quantity == 0
        assert warehouse_record1.opening_total_amount == 0
        assert warehouse_record1.quantity_recorded == 120
        assert warehouse_record1.unit_price == 100
        assert warehouse_record1.closing_quantity == 120
        assert warehouse_record1.closing_total_amount == 12000

        warehouse_record2 = WarehouseRecord.objects.get(
            warehouse_item__item=purchase_item.item, record_type='REMOVE', removal_type='INVENTORY')

        assert warehouse_record2.quantity_recorded == purchase_item.quantity_to_inventory
        assert warehouse_record2.unit_price == purchase_item.recommended_retail_price
        assert warehouse_record2.warehouse_item.item == purchase_item.item
        assert warehouse_record2.record_type == 'REMOVE'
        assert warehouse_record2.removal_type == 'INVENTORY'
        assert warehouse_record2.removal_quantity_leaving_warehouse == purchase_item.quantity_to_inventory_on_display    # noqa
        assert warehouse_record2.removal_quantity_remaining_in_warehouse == purchase_item.quantity_to_inventory_in_warehouse # noqa

        assert warehouse_record2.opening_quantity == 120
        assert warehouse_record2.opening_total_amount == 12000
        assert warehouse_record2.quantity_recorded == 40
        assert warehouse_record2.unit_price == 100
        assert warehouse_record2.closing_quantity == 80
        assert warehouse_record2.closing_total_amount == 8000

        inventory_record1 = InventoryRecord.objects.get(
            inventory__inventory_type='AVAILABLE', inventory_item__item=purchase_item.item, record_type='ADD')
        assert inventory_record1.quantity_recorded == warehouse_record2.quantity_recorded == 40
        assert inventory_record1.unit_price == warehouse_record2.unit_price == 100
        assert inventory_record1.total_amount_recorded == warehouse_record2.total_amount_recorded == 4000    # noqa
        assert inventory_record1.quantity_of_stock_on_display == warehouse_record2.removal_quantity_leaving_warehouse == 10  # noqa
        assert inventory_record1.quantity_of_stock_in_warehouse == warehouse_record2.removal_quantity_remaining_in_warehouse == 30   # noqa

    def test_create_purchase_record_no_transfer_to_inventory(self):
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
        baker.make(
            Warehouse, warehouse_name='Elites Private Warehouse', is_default=True,
            is_active=True, enterprise=enterprise_code)
        supplier = baker.make(Enterprise, name='LG Supplier')
        purchase = baker.make(
            Purchase, invoice_number='INV-001', supplier=supplier, enterprise=enterprise_code)
        purchase_item = baker.make(
            PurchaseItem, purchase=purchase, item=item, quantity_purchased=10, total_price=10000,
            enterprise=enterprise_code)

        purchase_item.refresh_from_db()
        assert float(purchase_item.unit_price) == 83.34

        assert WarehouseItem.objects.count() == 1
        assert WarehouseRecord.objects.count() == 1

        warehouse_record = WarehouseRecord.objects.get(warehouse_item__item=purchase_item.item)

        assert warehouse_record.quantity_recorded == 120
        assert warehouse_record.quantity_recorded == purchase_item.sale_units_purchased
        assert warehouse_record.unit_price == purchase_item.recommended_retail_price
