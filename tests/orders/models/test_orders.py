"""Test orders models file."""

import pytest

from django.test import TestCase
from django.utils import timezone
from django.forms import ValidationError

from elites_franchise_portal.franchises.models import Franchise
from elites_franchise_portal.items.models import (
    Brand, BrandItemType, Category, Item, ItemModel, ItemType,
    ItemUnits, UnitsItemType, Units)
from elites_franchise_portal.debit.models import (
    Inventory, InventoryInventoryItem,
    InventoryItem, InventoryRecord, Warehouse, WarehouseItem,
    WarehouseWarehouseItem, WarehouseRecord)
from elites_franchise_portal.catalog.models import CatalogItem
from elites_franchise_portal.orders.models import (
    Cart, CartItem, Order, InstantOrderItem, InstallmentsOrderItem,
    Installment)
from elites_franchise_portal.customers.models import Customer

from model_bakery import baker
from model_bakery.recipe import Recipe


class TestOrder(TestCase):
    """."""

    def test_create_order(self):
        """."""
        franchise = baker.make(
            Franchise, reg_no='BS-9049444', name='Franchise1',
            elites_code='EAG-F/EAS-MB/22001-01', partnership_type='SUPERMARKET')
        franchise_code = franchise.elites_code
        customer = baker.make(
            Customer, customer_number=9876, first_name='John',
            last_name='Wick', other_names='Baba Yaga',
            phone_no='+254712345678', email='johnwick@parabellum.com')
        order = baker.make(Order, customer=customer, franchise=franchise_code)
        assert order
        assert Order.objects.count() == 1

    def test_process_order(self):
        """."""
        franchise = baker.make(Franchise, name='Elites Age Supermarket')
        franchise_code = franchise.elites_code
        baker.make(
            Inventory, inventory_name='Elites Working Inventory', is_master=True,
            inventory_type='WORKING STOCK', franchise=franchise_code)
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
            ItemModel, brand=brand, item_type=item_type, model_name='GE731K-B/SUT',
            franchise=franchise_code)
        item_model2 = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731L-C/SUT',
            franchise=franchise_code)
        item_model3 = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731M-D/SUT',
            franchise=franchise_code)
        item_model4 = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731N-E/SUT',
            franchise=franchise_code)
        item1 = baker.make(
            Item, item_model=item_model1, barcode='838383885673', make_year=2020,
            franchise=franchise_code)
        item2 = baker.make(
            Item, item_model=item_model2, barcode='838380987383', make_year=2020,
            franchise=franchise_code)
        item3 = baker.make(
            Item, item_model=item_model3, barcode='678838383883', make_year=2020,
            franchise=franchise_code)
        item4 = baker.make(
            Item, item_model=item_model4, barcode='838383887654', make_year=2020,
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
            ItemUnits, item=item1, sales_units=s_units, purchases_units=p_units,
            items_per_purchase_unit=12, franchise=franchise_code)
        baker.make(
            ItemUnits, item=item2, sales_units=s_units, purchases_units=p_units,
            items_per_purchase_unit=12, franchise=franchise_code)
        baker.make(
            ItemUnits, item=item3, sales_units=s_units, purchases_units=p_units,
            items_per_purchase_unit=12, franchise=franchise_code)
        baker.make(
            ItemUnits, item=item4, sales_units=s_units, purchases_units=p_units,
            items_per_purchase_unit=12, franchise=franchise_code)
        inventory_item1 = InventoryItem.objects.get(item=item1, franchise=franchise_code)
        inventory_item2 = InventoryItem.objects.get(item=item2, franchise=franchise_code)
        inventory_item3 = InventoryItem.objects.get(item=item3, franchise=franchise_code)
        inventory_item4 = InventoryItem.objects.get(item=item4, franchise=franchise_code)
        inventory = baker.make(
            Inventory, inventory_name='Elites Available Inventory', inventory_type='AVAILABLE',
            franchise=franchise_code)
        baker.make(InventoryInventoryItem, inventory=inventory, inventory_item=inventory_item1)
        baker.make(InventoryInventoryItem, inventory=inventory, inventory_item=inventory_item2)
        baker.make(InventoryInventoryItem, inventory=inventory, inventory_item=inventory_item3)
        baker.make(InventoryInventoryItem, inventory=inventory, inventory_item=inventory_item4)
        baker.make(
            InventoryRecord, inventory=inventory, inventory_item=inventory_item1, record_type='ADD',
            quantity_recorded=20, unit_price=350,
            franchise=franchise_code)
        baker.make(
            InventoryRecord, inventory=inventory, inventory_item=inventory_item2, record_type='ADD',
            quantity_recorded=10, unit_price=1000,
            franchise=franchise_code)
        baker.make(
            InventoryRecord, inventory=inventory, inventory_item=inventory_item3, record_type='ADD',
            quantity_recorded=5, unit_price=2750,
            franchise=franchise_code)
        baker.make(
            InventoryRecord, inventory=inventory, inventory_item=inventory_item4, record_type='ADD',
            quantity_recorded=5, unit_price=2950,
            franchise=franchise_code)
        catalog_item1 = baker.make(
            CatalogItem, inventory_item=inventory_item1, franchise=franchise_code)
        catalog_item2 = baker.make(
            CatalogItem, inventory_item=inventory_item2, franchise=franchise_code)
        catalog_item3 = baker.make(
            CatalogItem, inventory_item=inventory_item3, franchise=franchise_code)
        customer = baker.make(
            Customer, customer_number=9876, first_name='John',
            last_name='Wick', other_names='Baba Yaga',
            phone_no='+254712345678', email='johnwick@parabellum.com')
        cart = baker.make(
            Cart, cart_code='EAS-C-10001', customer=customer, franchise=franchise_code)
        cart_item1 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item1, quantity_added=3,
            franchise=franchise_code)
        cart_item2 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item2, quantity_added=1,
            franchise=franchise_code)
        cart_item3 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item3, quantity_added=3,
            franchise=franchise_code)
        order = baker.make(Order, customer=customer, franchise=franchise_code)
        instant_order_item = baker.make(
            InstantOrderItem, order=order, franchise=franchise.elites_code,
            cart_item=cart_item1, confirmation_status='CONFIRMED', amount_paid=350)
        installment_order_item1 = baker.make(
            InstallmentsOrderItem, franchise=franchise.elites_code, deposit_amount=200,
            order=order, cart_item=cart_item2, confirmation_status='CONFIRMED')
        installment_order_item2 = baker.make(
            InstallmentsOrderItem, franchise=franchise.elites_code, deposit_amount=800,
            order=order, cart_item=cart_item3, confirmation_status='CONFIRMED')
        assert order.is_processed == False   # noqa
        assert instant_order_item
        assert installment_order_item1
        assert installment_order_item2
        order.process_order()
        order.refresh_from_db()
        assert order.is_processed == True    # noqa

    def test_fail_process_empty_order(self):
        """."""
        customer = baker.make(
            Customer, customer_number=9876, first_name='John',
            last_name='Wick', other_names='Baba Yaga',
            phone_no='+254712345678', email='johnwick@parabellum.com')
        franchise = baker.make(
            Franchise, reg_no='BS-9049444', name='Franchise1',
            elites_code='EAG-F/EAS-MB/22001-01', partnership_type='SUPERMARKET')
        franchise_code = franchise.elites_code
        order = baker.make(Order, customer=customer, franchise=franchise_code)

        with pytest.raises(ValidationError) as ve:
            order.process_order()
        msg = 'The order is empty. Please add an item to cart and complete your order.'
        assert msg in ve.value.messages


class TestInsantOrderItem(TestCase):
    """."""

    def test_create_instant_order_item(self):
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
        s_units = baker.make(Units, units_name='5 Gas', franchise=franchise_code)
        baker.make(UnitsItemType, item_type=item_type, units=s_units, franchise=franchise_code)
        s_units.item_types.set([item_type])
        s_units.save()
        p_units = baker.make(Units, units_name='5 Gas', franchise=franchise_code)
        baker.make(UnitsItemType, item_type=item_type, units=p_units, franchise=franchise_code)
        p_units.item_types.set([item_type])
        p_units.save()
        baker.make(
            ItemUnits, item=item, sales_units=s_units, purchases_units=p_units,
            items_per_purchase_unit=1, franchise=franchise_code)
        inventory_item = InventoryItem.objects.get(item=item, franchise=franchise_code)
        baker.make(
            InventoryRecord, inventory_item=inventory_item, record_type='ADD',
            quantity_recorded=20, unit_price=350, franchise=franchise_code)
        catalog_item = baker.make(
            CatalogItem, inventory_item=inventory_item, franchise=franchise_code)
        customer = baker.make(
            Customer, customer_number=9876, first_name='John',
            last_name='Wick', other_names='Baba Yaga',
            phone_no='+254712345678', email='johnwick@parabellum.com')
        cart = baker.make(
            Cart, cart_code='EAS-C-10001', customer=customer, franchise=franchise_code)
        cart_item = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item, quantity_added=2,
            franchise=franchise_code)
        order = baker.make(Order, customer=customer, franchise=franchise_code)
        instant_order_item = baker.make(
            InstantOrderItem, order=order, franchise=franchise.elites_code,
            cart_item=cart_item, confirmation_status='CONFIRMED', amount_paid=350)
        assert instant_order_item
        assert InstantOrderItem.objects.count() == 1

    def test_create_instant_order_items_more_than_available_quantity(self):
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
        brand_item_type = baker.make(
            BrandItemType, brand=brand, item_type=item_type,
            franchise=franchise_code)
        item_model = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731K-B SUT',
            franchise=franchise_code)
        item = baker.make(
            Item, item_model=item_model, barcode='83838388383', make_year=2020,
            franchise=franchise_code)
        s_units = baker.make(Units, units_name='5 Gas', franchise=franchise_code)
        baker.make(UnitsItemType, item_type=item_type, units=s_units, franchise=franchise_code)
        s_units.item_types.set([item_type])
        s_units.save()
        p_units = baker.make(Units, units_name='5 Gas', franchise=franchise_code)
        baker.make(UnitsItemType, item_type=item_type, units=p_units, franchise=franchise_code)
        p_units.item_types.set([item_type])
        p_units.save()
        baker.make(
            ItemUnits, item=item, sales_units=s_units, purchases_units=p_units,
            items_per_purchase_unit=1, franchise=franchise_code)

        warehouse = baker.make(
            Warehouse, warehouse_name='Elites Default Warehouse', franchise=franchise_code)
        warehouse_item = baker.make(WarehouseItem, item=item, franchise=franchise_code)
        baker.make(
            WarehouseRecord, warehouse=warehouse, warehouse_item=warehouse_item,
            record_type='ADD', quantity_recorded=30, unit_price=300, franchise=franchise_code)
        inventory_item = InventoryItem.objects.get(item=item, franchise=franchise_code)
        baker.make(
            InventoryRecord, inventory_item=inventory_item, record_type='ADD',
            quantity_recorded=20, unit_price=350, franchise=franchise_code)
        catalog_item = baker.make(
            CatalogItem, inventory_item=inventory_item, franchise=franchise_code)
        customer = baker.make(
            Customer, customer_number=9876, first_name='John',
            last_name='Wick', other_names='Baba Yaga',
            phone_no='+254712345678', email='johnwick@parabellum.com')
        cart = baker.make(
            Cart, cart_code='EAS-C-10001', customer=customer, franchise=franchise_code)
        cart_item = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item, quantity_added=25,
            franchise=franchise_code)
        order = baker.make(Order, customer=customer, franchise=franchise_code)
        instant_order_item = baker.make(
            InstantOrderItem, order=order, franchise=franchise.elites_code,
            cart_item=cart_item, confirmation_status='CONFIRMED', amount_paid=350)
        assert instant_order_item
        assert InstantOrderItem.objects.count() == 1

    def test_fail_create_instant_order_items_more_than_available_quantity(self):
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
        brand_item_type = baker.make(
            BrandItemType, brand=brand, item_type=item_type,
            franchise=franchise_code)
        item_model = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731K-B SUT',
            franchise=franchise_code)
        item = baker.make(
            Item, item_model=item_model, barcode='83838388383', make_year=2020,
            franchise=franchise_code)
        s_units = baker.make(Units, units_name='5 Gas', franchise=franchise_code)
        baker.make(UnitsItemType, item_type=item_type, units=s_units, franchise=franchise_code)
        s_units.item_types.set([item_type])
        s_units.save()
        p_units = baker.make(Units, units_name='5 Gas', franchise=franchise_code)
        baker.make(UnitsItemType, item_type=item_type, units=p_units, franchise=franchise_code)
        p_units.item_types.set([item_type])
        p_units.save()
        baker.make(
            ItemUnits, item=item, sales_units=s_units, purchases_units=p_units,
            items_per_purchase_unit=1, franchise=franchise_code)
        warehouse = baker.make(
            Warehouse, warehouse_name='Elites Default Warehouse', is_default=True,
            franchise=franchise_code)
        warehouse_item = baker.make(WarehouseItem, item=item, franchise=franchise_code)
        baker.make(
            WarehouseRecord, warehouse=warehouse, warehouse_item=warehouse_item, record_type='ADD',
            quantity_recorded=30, unit_price=300, franchise=franchise_code)
        inventory = baker.make(
            Inventory, inventory_name='Elites Age Supermarket Working Stock Inventory',
            inventory_type='WORKING STOCK', franchise=franchise_code)
        inventory_item = InventoryItem.objects.get(item=item, franchise=franchise_code)
        baker.make(
            InventoryRecord, inventory=inventory, inventory_item=inventory_item, record_type='ADD',
            quantity_recorded=20, unit_price=350, franchise=franchise_code)
        catalog_item = baker.make(
            CatalogItem, inventory_item=inventory_item, franchise=franchise_code)
        customer = baker.make(
            Customer, customer_number=9876, first_name='John',
            last_name='Wick', other_names='Baba Yaga',
            phone_no='+254712345678', email='johnwick@parabellum.com')
        cart = baker.make(
            Cart, cart_code='EAS-C-10001', customer=customer, franchise=franchise_code)
        cart_item = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item, quantity_added=35,
            franchise=franchise_code)
        order = baker.make(Order, customer=customer, franchise=franchise_code)
        instant_order_item_recipe = Recipe(
            InstantOrderItem, order=order, franchise=franchise.elites_code,
            cart_item=cart_item, confirmation_status='CONFIRMED', amount_paid=350)

        with pytest.raises(ValidationError) as ve:
            instant_order_item_recipe.make()
        msg = 'There are not enough items in warehouse to fulfil this order'
        assert msg in ve.value.messages


class TestInstallmentOrderItem(TestCase):
    """."""

    def test_create_installments_order(self):
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
        brand_item_type = baker.make(
            BrandItemType, brand=brand, item_type=item_type,
            franchise=franchise_code)
        item_model = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731K-B SUT',
            franchise=franchise_code)
        item = baker.make(
            Item, item_model=item_model, barcode='83838388383', make_year=2020,
            franchise=franchise_code)
        s_units = baker.make(Units, units_name='5 Gas', franchise=franchise_code)
        baker.make(UnitsItemType, item_type=item_type, units=s_units, franchise=franchise_code)
        s_units.item_types.set([item_type])
        s_units.save()
        p_units = baker.make(Units, units_name='5 Gas', franchise=franchise_code)
        baker.make(UnitsItemType, item_type=item_type, units=p_units, franchise=franchise_code)
        p_units.item_types.set([item_type])
        p_units.save()
        baker.make(
            ItemUnits, item=item, sales_units=s_units, purchases_units=p_units,
            items_per_purchase_unit=1, franchise=franchise_code)
        inventory_item = InventoryItem.objects.get(item=item, franchise=franchise_code)
        baker.make(
            InventoryRecord, inventory_item=inventory_item, record_type='ADD',
            quantity_recorded=20, unit_price=350, franchise=franchise_code)
        catalog_item = baker.make(
            CatalogItem, inventory_item=inventory_item, franchise=franchise_code)
        customer = baker.make(
            Customer, customer_number=9876, first_name='John',
            last_name='Wick', other_names='Baba Yaga',
            phone_no='+254712345678', email='johnwick@parabellum.com')
        cart = baker.make(
            Cart, cart_code='EAS-C-10001', customer=customer, franchise=franchise_code)
        cart_item = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item, quantity_added=2,
            franchise=franchise_code)
        order = baker.make(Order, customer=customer, franchise=franchise_code)
        installment_order_item = baker.make(
            InstallmentsOrderItem, order=order, cart_item=cart_item,
            confirmation_status='CONFIRMED', amount_paid=150, deposit_amount=150,
            franchise=franchise_code)

        assert installment_order_item
        assert InstallmentsOrderItem.objects.count() == 1

    def test_get_minimum_deposit_installments_order_no_deposit(self):
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
        brand_item_type = baker.make(
            BrandItemType, brand=brand, item_type=item_type,
            franchise=franchise_code)
        item_model = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731K-B SUT',
            franchise=franchise_code)
        item = baker.make(
            Item, item_model=item_model, barcode='83838388383', make_year=2020,
            franchise=franchise_code)
        s_units = baker.make(Units, units_name='5 Gas', franchise=franchise_code)
        baker.make(UnitsItemType, item_type=item_type, units=s_units, franchise=franchise_code)
        s_units.item_types.set([item_type])
        s_units.save()
        p_units = baker.make(Units, units_name='5 Gas', franchise=franchise_code)
        baker.make(UnitsItemType, item_type=item_type, units=p_units, franchise=franchise_code)
        p_units.item_types.set([item_type])
        p_units.save()
        baker.make(
            ItemUnits, item=item, sales_units=s_units, purchases_units=p_units,
            items_per_purchase_unit=1, franchise=franchise_code)
        inventory_item = InventoryItem.objects.get(item=item, franchise=franchise_code)
        baker.make(
            InventoryRecord, inventory_item=inventory_item, record_type='ADD',
            quantity_recorded=20, unit_price=350, franchise=franchise_code)
        catalog_item = baker.make(
            CatalogItem, inventory_item=inventory_item, franchise=franchise_code)
        customer = baker.make(
            Customer, customer_number=9876, first_name='John',
            last_name='Wick', other_names='Baba Yaga',
            phone_no='+254712345678', email='johnwick@parabellum.com')
        cart = baker.make(
            Cart, cart_code='EAS-C-10001', customer=customer, franchise=franchise_code)
        cart_item = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item, quantity_added=2,
            franchise=franchise_code)
        order = baker.make(Order, customer=customer, franchise=franchise_code)
        installment_order_item = baker.make(
            InstallmentsOrderItem, franchise=franchise.elites_code,
            order=order, cart_item=cart_item,  confirmation_status='CONFIRMED')

        assert installment_order_item.minimum_deposit == 140


    def test_get_minimum_deposit_multiple_installments_order_no_deposit(self):  # noqa
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
        brand_item_type = baker.make(
            BrandItemType, brand=brand, item_type=item_type,
            franchise=franchise_code)
        item_model1 = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731K-B/SUT',
            franchise=franchise_code)
        item_model2 = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731L-C/SUT',
            franchise=franchise_code)
        item_model3 = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731M-D/SUT',
            franchise=franchise_code)
        item_model4 = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731N-E/SUT',
            franchise=franchise_code)
        item1 = baker.make(
            Item, item_model=item_model1, barcode='838383885673', make_year=2020,
            franchise=franchise_code)
        item2 = baker.make(
            Item, item_model=item_model2, barcode='838380987383', make_year=2020,
            franchise=franchise_code)
        item3 = baker.make(
            Item, item_model=item_model3, barcode='678838383883', make_year=2020,
            franchise=franchise_code)
        item4 = baker.make(
            Item, item_model=item_model4, barcode='838383887654', make_year=2020,
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
            ItemUnits, item=item1, sales_units=s_units, purchases_units=p_units,
            items_per_purchase_unit=12, franchise=franchise_code)
        baker.make(
            ItemUnits, item=item2, sales_units=s_units, purchases_units=p_units,
            items_per_purchase_unit=12, franchise=franchise_code)
        baker.make(
            ItemUnits, item=item3, sales_units=s_units, purchases_units=p_units,
            items_per_purchase_unit=12, franchise=franchise_code)
        baker.make(
            ItemUnits, item=item4, sales_units=s_units, purchases_units=p_units,
            items_per_purchase_unit=12, franchise=franchise_code)
        inventory_item1 = InventoryItem.objects.get(item=item1, franchise=franchise_code)
        inventory_item2 = InventoryItem.objects.get(item=item2, franchise=franchise_code)
        inventory_item3 = InventoryItem.objects.get(item=item3, franchise=franchise_code)
        inventory_item4 = InventoryItem.objects.get(item=item4, franchise=franchise_code)
        baker.make(
            InventoryRecord, inventory_item=inventory_item1, record_type='ADD',
            quantity_recorded=20, unit_price=350, franchise=franchise_code)
        baker.make(
            InventoryRecord, inventory_item=inventory_item2, record_type='ADD',
            quantity_recorded=10, unit_price=1000, franchise=franchise_code)
        baker.make(
            InventoryRecord, inventory_item=inventory_item3, record_type='ADD',
            quantity_recorded=5, unit_price=2750, franchise=franchise_code)
        catalog_item1 = baker.make(
            CatalogItem, inventory_item=inventory_item1, franchise=franchise_code)
        catalog_item2 = baker.make(
            CatalogItem, inventory_item=inventory_item2, franchise=franchise_code)
        catalog_item3 = baker.make(
            CatalogItem, inventory_item=inventory_item3, franchise=franchise_code)
        customer = baker.make(
            Customer, customer_number=9876, first_name='John',
            last_name='Wick', other_names='Baba Yaga',
            phone_no='+254712345678', email='johnwick@parabellum.com')
        cart = baker.make(
            Cart, cart_code='EAS-C-10001', customer=customer, franchise=franchise_code)
        cart_item1 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item1, quantity_added=7,
            franchise=franchise_code)
        cart_item2 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item2, quantity_added=4,
            franchise=franchise_code)
        cart_item3 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item3, quantity_added=2,
            franchise=franchise_code)
        order = baker.make(Order, customer=customer, franchise=franchise_code)
        installment_order_item1 = baker.make(
            InstallmentsOrderItem, franchise=franchise.elites_code,
            order=order, cart_item=cart_item1,  confirmation_status='CONFIRMED')
        installment_order_item2 = baker.make(
            InstallmentsOrderItem, franchise=franchise.elites_code,
            order=order, cart_item=cart_item2,  confirmation_status='CONFIRMED')
        installment_order_item3 = baker.make(
            InstallmentsOrderItem, franchise=franchise.elites_code,
            order=order, cart_item=cart_item3,  confirmation_status='CONFIRMED')

        assert installment_order_item1.deposit_amount == 0
        assert installment_order_item2.deposit_amount == 0
        assert installment_order_item3.deposit_amount == 0

        assert installment_order_item1.minimum_deposit == 490
        assert installment_order_item2.minimum_deposit == 800
        assert installment_order_item3.minimum_deposit == 1100

    def test_create_installment_item_no_deposit_instant_order_item_present(self):
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
        brand_item_type = baker.make(
            BrandItemType, brand=brand, item_type=item_type,
            franchise=franchise_code)
        item_model1 = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731K-B/SUT',
            franchise=franchise_code)
        item_model2 = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731L-C/SUT',
            franchise=franchise_code)
        item_model3 = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731M-D/SUT',
            franchise=franchise_code)
        item_model4 = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731N-E/SUT',
            franchise=franchise_code)
        item1 = baker.make(
            Item, item_model=item_model1, barcode='838383885673', make_year=2020,
            franchise=franchise_code)
        item2 = baker.make(
            Item, item_model=item_model2, barcode='838380987383', make_year=2020,
            franchise=franchise_code)
        item3 = baker.make(
            Item, item_model=item_model3, barcode='678838383883', make_year=2020,
            franchise=franchise_code)
        item4 = baker.make(
            Item, item_model=item_model4, barcode='838383887654', make_year=2020,
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
            ItemUnits, item=item1, sales_units=s_units, purchases_units=p_units,
            items_per_purchase_unit=12, franchise=franchise_code)
        baker.make(
            ItemUnits, item=item2, sales_units=s_units, purchases_units=p_units,
            items_per_purchase_unit=12, franchise=franchise_code)
        baker.make(
            ItemUnits, item=item3, sales_units=s_units, purchases_units=p_units,
            items_per_purchase_unit=12, franchise=franchise_code)
        baker.make(
            ItemUnits, item=item4, sales_units=s_units, purchases_units=p_units,
            items_per_purchase_unit=12, franchise=franchise_code)
        inventory_item1 = InventoryItem.objects.get(item=item1, franchise=franchise_code)
        inventory_item2 = InventoryItem.objects.get(item=item2, franchise=franchise_code)
        inventory_item3 = InventoryItem.objects.get(item=item3, franchise=franchise_code)
        inventory_item4 = InventoryItem.objects.get(item=item4, franchise=franchise_code)
        baker.make(
            InventoryRecord, inventory_item=inventory_item1, record_type='ADD',
            quantity_recorded=20, unit_price=350, franchise=franchise_code)
        baker.make(
            InventoryRecord, inventory_item=inventory_item2, record_type='ADD',
            quantity_recorded=10, unit_price=1000, franchise=franchise_code)
        baker.make(
            InventoryRecord, inventory_item=inventory_item3, record_type='ADD',
            quantity_recorded=5, unit_price=2750, franchise=franchise_code)
        catalog_item1 = baker.make(
            CatalogItem, inventory_item=inventory_item1, franchise=franchise_code)
        catalog_item2 = baker.make(
            CatalogItem, inventory_item=inventory_item2, franchise=franchise_code)
        catalog_item3 = baker.make(
            CatalogItem, inventory_item=inventory_item3, franchise=franchise_code)
        customer = baker.make(
            Customer, customer_number=9876, first_name='John',
            last_name='Wick', other_names='Baba Yaga',
            phone_no='+254712345678', email='johnwick@parabellum.com')
        cart = baker.make(
            Cart, cart_code='EAS-C-10001', customer=customer, franchise=franchise_code)
        cart_item1 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item1, quantity_added=1,
            franchise=franchise_code)
        cart_item2 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item2, quantity_added=1,
            franchise=franchise_code)
        cart_item3 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item3, quantity_added=4,
            franchise=franchise_code)
        order = baker.make(Order, customer=customer, franchise=franchise_code)
        instant_order_item1 = baker.make(
            InstantOrderItem, order=order, franchise=franchise.elites_code,
            cart_item=cart_item1, confirmation_status='CONFIRMED', amount_paid=350)
        instant_order_item2 = baker.make(
            InstantOrderItem, order=order, franchise=franchise.elites_code,
            cart_item=cart_item2, confirmation_status='CONFIRMED', amount_paid=350)
        installment_order_item = baker.make(
            InstallmentsOrderItem, franchise=franchise.elites_code,
            order=order, cart_item=cart_item3,  confirmation_status='CONFIRMED')

        instant_total = float(instant_order_item1.total_amount + instant_order_item2.total_amount)
        set_min_deposit = 0.2 * float(installment_order_item.total_amount)
        remaining_min_deposit = set_min_deposit - instant_total
        assert installment_order_item.minimum_deposit == remaining_min_deposit == 850

    def test_get_minimum_deposit_for_installment_item_with_deposit_and_instant_order_item_present(self):    # noqa
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
        brand_item_type = baker.make(
            BrandItemType, brand=brand, item_type=item_type,
            franchise=franchise_code)
        item_model1 = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731K-B/SUT',
            franchise=franchise_code)
        item_model2 = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731L-C/SUT',
            franchise=franchise_code)
        item_model3 = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731M-D/SUT',
            franchise=franchise_code)
        item_model4 = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731N-E/SUT',
            franchise=franchise_code)
        item1 = baker.make(
            Item, item_model=item_model1, barcode='838383885673', make_year=2020,
            franchise=franchise_code)
        item2 = baker.make(
            Item, item_model=item_model2, barcode='838380987383', make_year=2020,
            franchise=franchise_code)
        item3 = baker.make(
            Item, item_model=item_model3, barcode='678838383883', make_year=2020,
            franchise=franchise_code)
        item4 = baker.make(
            Item, item_model=item_model4, barcode='838383887654', make_year=2020,
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
            ItemUnits, item=item1, sales_units=s_units, purchases_units=p_units,
            items_per_purchase_unit=12, franchise=franchise_code)
        baker.make(
            ItemUnits, item=item2, sales_units=s_units, purchases_units=p_units,
            items_per_purchase_unit=12, franchise=franchise_code)
        baker.make(
            ItemUnits, item=item3, sales_units=s_units, purchases_units=p_units,
            items_per_purchase_unit=12, franchise=franchise_code)
        baker.make(
            ItemUnits, item=item4, sales_units=s_units, purchases_units=p_units,
            items_per_purchase_unit=12, franchise=franchise_code)
        inventory_item1 = InventoryItem.objects.get(item=item1, franchise=franchise_code)
        inventory_item2 = InventoryItem.objects.get(item=item2, franchise=franchise_code)
        inventory_item3 = InventoryItem.objects.get(item=item3, franchise=franchise_code)
        inventory_item4 = InventoryItem.objects.get(item=item4, franchise=franchise_code)
        baker.make(
            InventoryRecord, inventory_item=inventory_item1, record_type='ADD',
            quantity_recorded=20, unit_price=350, franchise=franchise_code)
        baker.make(
            InventoryRecord, inventory_item=inventory_item2, record_type='ADD',
            quantity_recorded=10, unit_price=1000, franchise=franchise_code)
        baker.make(
            InventoryRecord, inventory_item=inventory_item3, record_type='ADD',
            quantity_recorded=5, unit_price=2750, franchise=franchise_code)
        catalog_item1 = baker.make(
            CatalogItem, inventory_item=inventory_item1, franchise=franchise_code)
        catalog_item2 = baker.make(
            CatalogItem, inventory_item=inventory_item2, franchise=franchise_code)
        catalog_item3 = baker.make(
            CatalogItem, inventory_item=inventory_item3, franchise=franchise_code)
        customer = baker.make(
            Customer, customer_number=9876, first_name='John',
            last_name='Wick', other_names='Baba Yaga',
            phone_no='+254712345678', email='johnwick@parabellum.com')
        cart = baker.make(
            Cart, cart_code='EAS-C-10001', customer=customer, franchise=franchise_code)
        cart_item1 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item1, quantity_added=3,
            franchise=franchise_code)
        cart_item2 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item2, quantity_added=1,
            franchise=franchise_code)
        cart_item3 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item3, quantity_added=3,
            franchise=franchise_code)
        order = baker.make(Order, customer=customer, franchise=franchise_code)
        instant_order_item = baker.make(
            InstantOrderItem, order=order, franchise=franchise.elites_code,
            cart_item=cart_item1, confirmation_status='CONFIRMED', amount_paid=350)
        installment_order_item1 = baker.make(
            InstallmentsOrderItem, franchise=franchise.elites_code, deposit_amount=200,
            order=order, cart_item=cart_item2, confirmation_status='CONFIRMED')
        installment_order_item2 = baker.make(
            InstallmentsOrderItem, franchise=franchise.elites_code, deposit_amount=800,
            order=order, cart_item=cart_item3, confirmation_status='CONFIRMED')

        instant_total = float(instant_order_item.total_amount)
        installment_item1_total = float(installment_order_item1.total_amount)
        installment_item2_total = float(installment_order_item2.total_amount)
        installment_item1_expected_deposit = 0.2 * installment_item1_total
        installment_item2_expected_deposit = 0.2 * installment_item2_total

        installment_items_total = installment_item1_total + installment_item2_total
        installment_item1_share_ratio = installment_item1_total/installment_items_total
        installment_item2_share_ratio = installment_item2_total/installment_items_total

        installment_item1_instant_total_share_amount = installment_item1_share_ratio * instant_total    # noqa
        installment_item2_instant_total_share_amount = installment_item2_share_ratio * instant_total    # noqa

        assert installment_item1_share_ratio + installment_item2_share_ratio == 1
        assert installment_item1_instant_total_share_amount + \
            installment_item2_instant_total_share_amount == instant_total

        installment_item1_remaining_deposit = installment_item1_expected_deposit - \
            installment_item1_instant_total_share_amount
        installment_item2_remaining_deposit = installment_item2_expected_deposit - installment_item2_instant_total_share_amount # noqa

        assert round(installment_order_item1.minimum_deposit, 2) == round(installment_item1_remaining_deposit, 2) == 86.49  # noqa
        assert round(installment_order_item2.minimum_deposit, 2) == round(installment_item2_remaining_deposit, 2) == 713.51 # noqa


class TestInstallment(TestCase):
    """."""

    def test_create_installments(self):
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
        brand_item_type = baker.make(
            BrandItemType, brand=brand, item_type=item_type,
            franchise=franchise_code)
        item_model = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731K-B SUT',
            franchise=franchise_code)
        item = baker.make(
            Item, item_model=item_model, barcode='83838388383', make_year=2020,
            franchise=franchise_code)
        s_units = baker.make(Units, units_name='5 Gas', franchise=franchise_code)
        baker.make(UnitsItemType, item_type=item_type, units=s_units, franchise=franchise_code)
        s_units.item_types.set([item_type])
        s_units.save()
        p_units = baker.make(Units, units_name='5 Gas', franchise=franchise_code)
        baker.make(UnitsItemType, item_type=item_type, units=p_units, franchise=franchise_code)
        p_units.item_types.set([item_type])
        p_units.save()
        baker.make(
            ItemUnits, item=item, sales_units=s_units, purchases_units=p_units,
            items_per_purchase_unit=1, franchise=franchise_code)
        inventory_item = InventoryItem.objects.get(item=item, franchise=franchise_code)
        baker.make(
            InventoryRecord, inventory_item=inventory_item, record_type='ADD',
            quantity_recorded=20, unit_price=350, franchise=franchise_code)
        catalog_item = baker.make(
            CatalogItem, inventory_item=inventory_item, franchise=franchise_code)
        customer = baker.make(
            Customer, customer_number=9876, first_name='John',
            last_name='Wick', other_names='Baba Yaga',
            phone_no='+254712345678', email='johnwick@parabellum.com')
        cart = baker.make(
            Cart, cart_code='EAS-C-10001', customer=customer, franchise=franchise_code)
        cart_item = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item, quantity_added=2,
            franchise=franchise_code)
        order = baker.make(Order, customer=customer, franchise=franchise_code)
        installment_order_item = baker.make(
            InstallmentsOrderItem, franchise=franchise.elites_code,
            order=order, cart_item=cart_item,  confirmation_status='CONFIRMED',
            amount_paid=150, deposit_amount=150)
        installment_date = timezone.now()
        installment = baker.make(
            Installment, installment_date=installment_date,
            installment_item=installment_order_item, amount=100,)

        assert installment
        assert Installment.objects.count() == 1

    def test_fail_create_installments_cleared_item(self):
        """."""
        franchise = baker.make(Franchise, name='Elites Age Supermarket')
        franchise_code = franchise.elites_code
        cat = baker.make(
            Category, category_name='Vehicles',
            franchise=franchise_code)
        item_type = baker.make(
            ItemType, category=cat, type_name='Car',
            franchise=franchise_code)
        brand = baker.make(
            Brand, brand_name='Ford', franchise=franchise_code)
        brand_item_type = baker.make(
            BrandItemType, brand=brand, item_type=item_type,
            franchise=franchise_code)
        item_model = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='Mustang Boss 429',
            franchise=franchise_code)
        item = baker.make(
            Item, item_model=item_model, barcode='345678987654', make_year=1969,
            franchise=franchise_code)
        s_units = baker.make(Units, units_name='500 horsepower', franchise=franchise_code)
        baker.make(UnitsItemType, item_type=item_type, units=s_units, franchise=franchise_code)
        s_units.item_types.set([item_type])
        s_units.save()
        p_units = baker.make(Units, units_name='500 horsepower', franchise=franchise_code)
        baker.make(UnitsItemType, item_type=item_type, units=p_units, franchise=franchise_code)
        p_units.item_types.set([item_type])
        p_units.save()
        baker.make(
            ItemUnits, item=item, sales_units=s_units, purchases_units=p_units,
            items_per_purchase_unit=1, franchise=franchise_code)
        inventory_item = InventoryItem.objects.get(item=item, franchise=franchise_code)
        baker.make(
            InventoryRecord, inventory_item=inventory_item, record_type='ADD',
            quantity_recorded=5, unit_price=35000, franchise=franchise_code)
        catalog_item = baker.make(
            CatalogItem, inventory_item=inventory_item, franchise=franchise_code)
        customer = baker.make(
            Customer, customer_number=9876, title='Mr', first_name='John',
            last_name='Wick', other_names='Baba Yaga', gender='MALE',
            phone_no='+254712345678', email='johnwick@parabellum.com')
        cart = baker.make(
            Cart, cart_code='EAS-C-10001', customer=customer, franchise=franchise_code)
        cart_item = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item, quantity_added=1,
            franchise=franchise_code)
        order = baker.make(Order, customer=customer, franchise=franchise_code)
        installment_order_item = baker.make(
            InstallmentsOrderItem, franchise=franchise_code,
            order=order, cart_item=cart_item,  confirmation_status='CONFIRMED',
            amount_paid=25000, deposit_amount=25000)
        installment1 = baker.make(
            Installment, installment_item=installment_order_item, amount=10000)
        installment2 = Recipe(
            Installment, installment_item=installment_order_item, amount=3000)

        with pytest.raises(ValidationError) as ve:
            installment2.make()
        msg = 'Please select a different item to process installments for Mr John Wick. His Ford Mustang Boss 429 Car is already cleared'   # noqa
        assert msg in ve.value.messages

        assert installment1
        assert Installment.objects.count() == 1
