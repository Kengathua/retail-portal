from django.test import TestCase

from elites_franchise_portal.franchises.models import Franchise
from elites_franchise_portal.items.models import (
    Brand, BrandItemType, Category, Item, ItemModel, ItemType,
    ItemUnits, UnitsItemType, Units)
from elites_franchise_portal.debit.models import (
    InventoryItem, InventoryRecord, WarehouseRecord, Warehouse, WarehouseItem)

from elites_franchise_portal.credit.models import Purchase

from model_bakery import baker


class TestPurchase(TestCase):
    """."""

    def test_create_purchase_record(self):
        """."""
        franchise = baker.make(
            Franchise, name='Franchise One', elites_code='EAL-F/FO-MB/2201-01',
            partnership_type='SHOP')
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
        baker.make(
            Warehouse, warehouse_name='Elites Private Warehouse', is_default=True,
            is_active=True, franchise=franchise_code)
        purchase = baker.make(
            Purchase, item=item, quantity_purchased=10, total_price=10000,
            unit_marked_price=100, quantity_to_inventory=40,
            quantity_to_inventory_on_display=10, quantity_to_inventory_in_warehouse=30,
            franchise=franchise_code)

        assert float(purchase.buying_unit_price) == 83.34

        assert Warehouse.objects.count() == 1
        assert WarehouseRecord.objects.count() == 2
        assert InventoryRecord.objects.count() == 1

        warehouse_record1 = WarehouseRecord.objects.get(
            warehouse_item__item=purchase.item, record_type='ADD')
        assert warehouse_record1.opening_quantity == 0
        assert warehouse_record1.opening_total_amount == 0
        assert warehouse_record1.quantity_recorded == 120
        assert warehouse_record1.unit_price == 100
        assert warehouse_record1.closing_quantity == 120
        assert warehouse_record1.closing_total_amount == 12000

        warehouse_record2 = WarehouseRecord.objects.get(
            warehouse_item__item=purchase.item, record_type='REMOVE', removal_type='INVENTORY')

        assert warehouse_record2.quantity_recorded == purchase.quantity_to_inventory
        assert warehouse_record2.unit_price == purchase.unit_marked_price
        assert warehouse_record2.warehouse_item.item == purchase.item
        assert warehouse_record2.record_type == 'REMOVE'
        assert warehouse_record2.removal_type == 'INVENTORY'
        assert warehouse_record2.removal_quantity_leaving_warehouse == purchase.quantity_to_inventory_on_display    # noqa
        assert warehouse_record2.removal_quantity_remaining_in_warehouse == purchase.quantity_to_inventory_in_warehouse # noqa

        assert warehouse_record2.opening_quantity == 120
        assert warehouse_record2.opening_total_amount == 12000
        assert warehouse_record2.quantity_recorded == 40
        assert warehouse_record2.unit_price == 100
        assert warehouse_record2.closing_quantity == 80
        assert warehouse_record2.closing_total_amount == 8000

        inventory_record = InventoryRecord.objects.get(
            inventory_item__item=purchase.item, record_type='ADD')
        assert inventory_record.quantity_recorded == warehouse_record2.quantity_recorded == 40
        assert inventory_record.unit_price == warehouse_record2.unit_price == 100
        assert inventory_record.total_amount_recorded == warehouse_record2.total_amount_recorded == 4000    # noqa
        assert inventory_record.quantity_of_stock_on_display == warehouse_record2.removal_quantity_leaving_warehouse == 10  # noqa
        assert inventory_record.quantity_of_stock_in_warehouse == warehouse_record2.removal_quantity_remaining_in_warehouse == 30   # noqa

    def test_create_purchase_record_no_transfer_to_inventory(self):
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
        baker.make(
            Warehouse, warehouse_name='Elites Private Warehouse', is_default=True,
            is_active=True, franchise=franchise_code)
        purchase = baker.make(
            Purchase, item=item, quantity_purchased=10, total_price=10000,
            franchise=franchise_code)

        assert float(purchase.buying_unit_price) == 83.34

        assert WarehouseItem.objects.count() == 1
        assert WarehouseRecord.objects.count() == 1

        store_record = WarehouseRecord.objects.get(warehouse_item__item=purchase.item)

        assert store_record.quantity_recorded == 120
        assert store_record.quantity_recorded == purchase.sale_units_purchased
        assert store_record.unit_price == purchase.unit_marked_price
