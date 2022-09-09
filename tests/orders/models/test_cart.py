"""Test cart models file."""

import uuid
import pytest

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from elites_franchise_portal.items.models import (
    Brand, BrandItemType, Category, Item, ItemModel, ItemType,
    ItemUnits, UnitsItemType, Units)
from elites_franchise_portal.debit.models import (
    Inventory, InventoryItem, InventoryRecord, InventoryInventoryItem)
from elites_franchise_portal.warehouses.models import (
    Warehouse, WarehouseItem, WarehouseWarehouseItem, WarehouseRecord)
from elites_franchise_portal.catalog.models import CatalogItem
from elites_franchise_portal.orders.models import (
    Cart, CartItem, Order, InstantOrderItem, InstallmentsOrderItem)
from elites_franchise_portal.enterprises.models import Enterprise
from elites_franchise_portal.customers.models import Customer

from model_bakery import baker


class TestCart(TestCase):
    """."""

    def test_create_cart(self):
        """."""
        enterprise = baker.make(Enterprise, name='Elites Age Supermarket')
        enterprise_code = enterprise.enterprise_code
        customer = baker.make(
            Customer, customer_number=9876, first_name='John', last_name='Wick',
            phone_no='+254712345678', email='johnwick@parabellum.com', enterprise=enterprise_code)
        cart = baker.make(
            Cart, customer=customer, cart_code='EAS-C-10001', enterprise=enterprise_code)

        assert cart
        assert Cart.objects.count() == 1

    def test_fail_checkout_empty_cart(self):
        """."""
        enterprise = baker.make(Enterprise, name='Elites Age Supermarket')
        enterprise_code = enterprise.enterprise_code
        customer = baker.make(
            Customer, customer_number=9876, first_name='John', last_name='Wick',
            phone_no='+254712345678', email='johnwick@parabellum.com', enterprise=enterprise_code)
        cart = baker.make(
            Cart, customer=customer, cart_code='EAS-C-10001', enterprise=enterprise_code)

        with pytest.raises(ValidationError) as ve:
            cart.checkout_cart()
        msg = 'Cart is empty. Please add items to checkout'
        assert msg in ve.value.messages

    def test_check_if_site_cart(self):
        """."""
        franchise = baker.make(Enterprise, name='Elites Age Supermarket')
        enterprise_code = franchise.enterprise_code
        test_user = get_user_model().objects.create_superuser(
            email='testuser@email.com', first_name='Test', last_name='User',
            guid=uuid.uuid4(), password='Testpass254$', enterprise=enterprise_code)
        customer = baker.make(
            Customer, customer_number=9876, first_name='John', last_name='Wick',
            is_enterprise=True, enterprise_user=test_user, phone_no='+254712345678',
            email='johnwick@parabellum.com', enterprise=enterprise_code)
        cart = baker.make(
            Cart, cart_code='EAS-C-10001', customer=customer, enterprise=enterprise_code)

        assert cart
        assert cart.is_enterprise
        assert Cart.objects.count() == 1

    def test_checkout_cart_instant_order_item(self):
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
            ItemModel, brand=brand, item_type=item_type, model_name='GE731K-B/SUT',
            enterprise=enterprise_code)
        item_model2 = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731L-C/SUT',
            enterprise=enterprise_code)
        item_model3 = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731M-D/SUT',
            enterprise=enterprise_code)
        item_model4 = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731N-E/SUT',
            enterprise=enterprise_code)
        item1 = baker.make(
            Item, item_model=item_model1, barcode='838383885673', make_year=2020,
            enterprise=enterprise_code)
        item2 = baker.make(
            Item, item_model=item_model2, barcode='838380987383', make_year=2020,
            enterprise=enterprise_code)
        item3 = baker.make(
            Item, item_model=item_model3, barcode='678838383883', make_year=2020,
            enterprise=enterprise_code)
        item4 = baker.make(
            Item, item_model=item_model4, barcode='838383887654', make_year=2020,
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
        baker.make(
            ItemUnits, item=item3, sales_units=s_units, purchases_units=p_units,
            quantity_of_sale_units_per_purchase_unit=12, enterprise=enterprise_code)
        baker.make(
            ItemUnits, item=item4, sales_units=s_units, purchases_units=p_units,
            quantity_of_sale_units_per_purchase_unit=12, enterprise=enterprise_code)
        master_inventory = baker.make(
            Inventory, inventory_name='Elites Working Inventory', is_master=True,
            inventory_type='WORKING STOCK', enterprise=enterprise_code)
        available_inventory = baker.make(
            Inventory, inventory_name='Available Inventory', is_master=False,
            inventory_type='AVAILABLE', enterprise=enterprise_code)
        inventory_item1 = baker.make(InventoryItem, item=item1, enterprise=enterprise_code)
        inventory_item2 = baker.make(InventoryItem, item=item2, enterprise=enterprise_code)
        inventory_item3 = baker.make(InventoryItem, item=item3, enterprise=enterprise_code)
        inventory_item4 = baker.make(InventoryItem, item=item4, enterprise=enterprise_code)

        baker.make(
            InventoryInventoryItem, inventory=master_inventory, inventory_item=inventory_item1)
        baker.make(
            InventoryInventoryItem, inventory=master_inventory, inventory_item=inventory_item2)
        baker.make(
            InventoryInventoryItem, inventory=master_inventory, inventory_item=inventory_item3)
        baker.make(
            InventoryInventoryItem, inventory=master_inventory, inventory_item=inventory_item4)

        baker.make(
            InventoryInventoryItem, inventory=available_inventory, inventory_item=inventory_item1)
        baker.make(
            InventoryInventoryItem, inventory=available_inventory, inventory_item=inventory_item2)
        baker.make(
            InventoryInventoryItem, inventory=available_inventory, inventory_item=inventory_item3)
        baker.make(
            InventoryInventoryItem, inventory=available_inventory, inventory_item=inventory_item4)

        baker.make(
            InventoryRecord, inventory=available_inventory, inventory_item=inventory_item1,
            record_type='ADD', quantity_recorded=20, unit_price=350, enterprise=enterprise_code)
        baker.make(
            InventoryRecord, inventory=available_inventory, inventory_item=inventory_item2,
            record_type='ADD', quantity_recorded=10, unit_price=1000, enterprise=enterprise_code)
        baker.make(
            InventoryRecord, inventory=available_inventory, inventory_item=inventory_item3,
            record_type='ADD', quantity_recorded=5, unit_price=2750, enterprise=enterprise_code)
        baker.make(
            InventoryRecord, inventory=available_inventory, inventory_item=inventory_item4,
            record_type='ADD', quantity_recorded=5, unit_price=2750, enterprise=enterprise_code)

        catalog_item1 = baker.make(
            CatalogItem, inventory_item=inventory_item1, enterprise=enterprise_code)
        catalog_item2 = baker.make(
            CatalogItem, inventory_item=inventory_item2, enterprise=enterprise_code)
        catalog_item3 = baker.make(
            CatalogItem, inventory_item=inventory_item3, enterprise=enterprise_code)
        catalog_item4 = baker.make(
            CatalogItem, inventory_item=inventory_item4, enterprise=enterprise_code)
        customer = baker.make(
            Customer, customer_number=9876, first_name='John', last_name='Wick',
            phone_no='+254712345678', email='johnwick@parabellum.com')
        cart = baker.make(
            Cart, cart_code='EAS-C-10001', customer=customer, enterprise=enterprise_code)
        cart_item1 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item1, quantity_added=3,
            enterprise=enterprise_code)
        cart_item2 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item2, quantity_added=1,
            enterprise=enterprise_code)
        cart_item3 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item3, quantity_added=3, is_installment=True,
            enterprise=enterprise_code)
        cart_item4 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item4, quantity_added=3, is_installment=True,
            enterprise=enterprise_code)
        cart.checkout_cart()

        assert cart_item1
        assert cart_item2
        assert cart_item3
        assert cart_item4
        assert Order.objects.count() == 1
        assert InstantOrderItem.objects.count() == 2
        assert InstallmentsOrderItem.objects.count() == 2

        order = Order.objects.get(customer=customer)
        customer.is_enterprise = True
        customer.save()
        cart.customer = customer
        cart.save()
        assert not order.is_enterprise
        cart.checkout_cart()
        order.refresh_from_db()
        assert order.is_enterprise

    def test_fail_checkout_specific_items_empyt_cart(self):
        """."""
        franchise = baker.make(Enterprise, name='Elites Age Supermarket')
        enterprise_code = franchise.enterprise_code
        customer = baker.make(
            Customer, customer_number=9876, first_name='John', last_name='Wick',
            phone_no='+254712345678', email='johnwick@parabellum.com',
            enterprise=enterprise_code)
        cart = baker.make(
            Cart, customer=customer, cart_code='EAS-C-10001', enterprise=enterprise_code)

        with pytest.raises(ValidationError) as ve:
            cart.checkout_specific_items_in_cart([])
        msg = 'Fast checkout cart is empty. Please add items to checkout'
        assert msg in ve.value.messages

    def test_checkout_specific_order_now_items_in_cart(self):
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
            ItemModel, brand=brand, item_type=item_type, model_name='GE731K-B/SUT',
            enterprise=enterprise_code)
        item_model2 = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731L-C/SUT',
            enterprise=enterprise_code)
        item_model3 = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731M-D/SUT',
            enterprise=enterprise_code)
        item_model4 = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731N-E/SUT',
            enterprise=enterprise_code)
        item1 = baker.make(
            Item, item_model=item_model1, barcode='838383885673', make_year=2020,
            enterprise=enterprise_code)
        item2 = baker.make(
            Item, item_model=item_model2, barcode='838380987383', make_year=2020,
            enterprise=enterprise_code)
        item3 = baker.make(
            Item, item_model=item_model3, barcode='678838383883', make_year=2020,
            enterprise=enterprise_code)
        item4 = baker.make(
            Item, item_model=item_model4, barcode='838383887654', make_year=2020,
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
        baker.make(
            ItemUnits, item=item3, sales_units=s_units, purchases_units=p_units,
            quantity_of_sale_units_per_purchase_unit=12, enterprise=enterprise_code)
        baker.make(
            ItemUnits, item=item4, sales_units=s_units, purchases_units=p_units,
            quantity_of_sale_units_per_purchase_unit=12, enterprise=enterprise_code)
        master_inventory = baker.make(
            Inventory, inventory_name='Elites Working Inventory', is_master=True,
            inventory_type='WORKING STOCK', enterprise=enterprise_code)
        available_inventory = baker.make(
            Inventory, inventory_name='Available Inventory', is_master=False,
            inventory_type='AVAILABLE', enterprise=enterprise_code)
        inventory_item1 = baker.make(InventoryItem, item=item1, enterprise=enterprise_code)
        inventory_item2 = baker.make(InventoryItem, item=item2, enterprise=enterprise_code)
        inventory_item3 = baker.make(InventoryItem, item=item3, enterprise=enterprise_code)
        inventory_item4 = baker.make(InventoryItem, item=item4, enterprise=enterprise_code)

        baker.make(
            InventoryInventoryItem, inventory=master_inventory, inventory_item=inventory_item1)
        baker.make(
            InventoryInventoryItem, inventory=master_inventory, inventory_item=inventory_item2)
        baker.make(
            InventoryInventoryItem, inventory=master_inventory, inventory_item=inventory_item3)
        baker.make(
            InventoryInventoryItem, inventory=master_inventory, inventory_item=inventory_item4)

        baker.make(
            InventoryInventoryItem, inventory=available_inventory, inventory_item=inventory_item1)
        baker.make(
            InventoryInventoryItem, inventory=available_inventory, inventory_item=inventory_item2)
        baker.make(
            InventoryInventoryItem, inventory=available_inventory, inventory_item=inventory_item3)
        baker.make(
            InventoryInventoryItem, inventory=available_inventory, inventory_item=inventory_item4)
        baker.make(
            InventoryRecord, inventory=available_inventory, inventory_item=inventory_item1,
            record_type='ADD', quantity_recorded=20, unit_price=350, enterprise=enterprise_code)
        baker.make(
            InventoryRecord, inventory=available_inventory, inventory_item=inventory_item2,
            record_type='ADD', quantity_recorded=10, unit_price=1000, enterprise=enterprise_code)
        baker.make(
            InventoryRecord, inventory=available_inventory, inventory_item=inventory_item3,
            record_type='ADD', quantity_recorded=5, unit_price=2750, enterprise=enterprise_code)
        baker.make(
            InventoryRecord, inventory=available_inventory, inventory_item=inventory_item4,
            record_type='ADD', quantity_recorded=5, unit_price=2750, enterprise=enterprise_code)
        catalog_item1 = baker.make(
            CatalogItem, inventory_item=inventory_item1, enterprise=enterprise_code)
        catalog_item2 = baker.make(
            CatalogItem, inventory_item=inventory_item2, enterprise=enterprise_code)
        catalog_item3 = baker.make(
            CatalogItem, inventory_item=inventory_item3, enterprise=enterprise_code)
        catalog_item4 = baker.make(
            CatalogItem, inventory_item=inventory_item4, enterprise=enterprise_code)
        customer = baker.make(
            Customer, customer_number=9876, first_name='John', last_name='Wick',
            phone_no='+254712345678', email='johnwick@parabellum.com')
        cart = baker.make(
            Cart, cart_code='EAS-C-10001', customer=customer, enterprise=enterprise_code)
        cart_item1 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item1, quantity_added=3, order_now=True,
            enterprise=enterprise_code)
        cart_item2 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item2, quantity_added=1,
            enterprise=enterprise_code)
        cart_item3 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item3, quantity_added=3, is_installment=True,
            order_now=True, enterprise=enterprise_code)
        cart_item4 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item4, quantity_added=3, is_installment=True,
            enterprise=enterprise_code)

        assert cart_item1
        assert cart_item2
        assert cart_item3
        assert cart_item4

        # checking out cart_item1 and cart_item3
        cart.checkout_specific_items_in_cart()

        assert Cart.objects.count() == 1
        assert CartItem.objects.count() == 4
        assert Order.objects.count() == 1
        assert InstantOrderItem.objects.count() == 1
        assert InstallmentsOrderItem.objects.count() == 1

        order = Order.objects.get(customer=customer)
        customer.is_enterprise = True
        customer.save()
        cart.customer = customer
        cart.save()
        assert not order.is_enterprise
        cart.checkout_cart()
        order.refresh_from_db()
        assert order.is_enterprise

    def test_checkout_selected_specific_items_in_cart(self):
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
            ItemModel, brand=brand, item_type=item_type, model_name='GE731K-B/SUT',
            enterprise=enterprise_code)
        item_model2 = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731L-C/SUT',
            enterprise=enterprise_code)
        item_model3 = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731M-D/SUT',
            enterprise=enterprise_code)
        item_model4 = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731N-E/SUT',
            enterprise=enterprise_code)
        item1 = baker.make(
            Item, item_model=item_model1, barcode='838383885673', make_year=2020,
            enterprise=enterprise_code)
        item2 = baker.make(
            Item, item_model=item_model2, barcode='838380987383', make_year=2020,
            enterprise=enterprise_code)
        item3 = baker.make(
            Item, item_model=item_model3, barcode='678838383883', make_year=2020,
            enterprise=enterprise_code)
        item4 = baker.make(
            Item, item_model=item_model4, barcode='838383887654', make_year=2020,
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
        baker.make(
            ItemUnits, item=item3, sales_units=s_units, purchases_units=p_units,
            quantity_of_sale_units_per_purchase_unit=12, enterprise=enterprise_code)
        baker.make(
            ItemUnits, item=item4, sales_units=s_units, purchases_units=p_units,
            quantity_of_sale_units_per_purchase_unit=12, enterprise=enterprise_code)
        master_inventory = baker.make(
            Inventory, inventory_name='Elites Working Inventory', is_master=True,
            inventory_type='WORKING STOCK', enterprise=enterprise_code)
        available_inventory = baker.make(
            Inventory, inventory_name='Available Inventory', is_master=False,
            inventory_type='AVAILABLE', enterprise=enterprise_code)
        inventory_item1 = baker.make(InventoryItem, item=item1, enterprise=enterprise_code)
        inventory_item2 = baker.make(InventoryItem, item=item2, enterprise=enterprise_code)
        inventory_item3 = baker.make(InventoryItem, item=item3, enterprise=enterprise_code)
        inventory_item4 = baker.make(InventoryItem, item=item4, enterprise=enterprise_code)

        baker.make(
            InventoryInventoryItem, inventory=master_inventory, inventory_item=inventory_item1)
        baker.make(
            InventoryInventoryItem, inventory=master_inventory, inventory_item=inventory_item2)
        baker.make(
            InventoryInventoryItem, inventory=master_inventory, inventory_item=inventory_item3)
        baker.make(
            InventoryInventoryItem, inventory=master_inventory, inventory_item=inventory_item4)

        baker.make(
            InventoryInventoryItem, inventory=available_inventory, inventory_item=inventory_item1)
        baker.make(
            InventoryInventoryItem, inventory=available_inventory, inventory_item=inventory_item2)
        baker.make(
            InventoryInventoryItem, inventory=available_inventory, inventory_item=inventory_item3)
        baker.make(
            InventoryInventoryItem, inventory=available_inventory, inventory_item=inventory_item4)
        baker.make(
            InventoryRecord, inventory=available_inventory, inventory_item=inventory_item1,
            record_type='ADD', quantity_recorded=20, unit_price=350, enterprise=enterprise_code)
        baker.make(
            InventoryRecord, inventory=available_inventory, inventory_item=inventory_item2,
            record_type='ADD', quantity_recorded=10, unit_price=1000, enterprise=enterprise_code)
        baker.make(
            InventoryRecord, inventory=available_inventory, inventory_item=inventory_item3,
            record_type='ADD', quantity_recorded=5, unit_price=2750, enterprise=enterprise_code)
        baker.make(
            InventoryRecord, inventory=available_inventory, inventory_item=inventory_item4,
            record_type='ADD', quantity_recorded=5, unit_price=2750, enterprise=enterprise_code)
        catalog_item1 = baker.make(
            CatalogItem, inventory_item=inventory_item1, enterprise=enterprise_code)
        catalog_item2 = baker.make(
            CatalogItem, inventory_item=inventory_item2, enterprise=enterprise_code)
        catalog_item3 = baker.make(
            CatalogItem, inventory_item=inventory_item3, enterprise=enterprise_code)
        catalog_item4 = baker.make(
            CatalogItem, inventory_item=inventory_item4, enterprise=enterprise_code)
        customer = baker.make(
            Customer, customer_number=9876, first_name='John', last_name='Wick',
            phone_no='+254712345678', email='johnwick@parabellum.com')
        cart = baker.make(
            Cart, cart_code='EAS-C-10001', customer=customer, enterprise=enterprise_code)
        cart_item1 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item1, quantity_added=3,
            enterprise=enterprise_code)
        cart_item2 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item2, quantity_added=1,
            enterprise=enterprise_code)
        cart_item3 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item3, quantity_added=3,
            is_installment=True, enterprise=enterprise_code)
        cart_item4 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item4, quantity_added=3,
            is_installment=True, enterprise=enterprise_code)

        assert cart_item1
        assert cart_item2
        assert cart_item3
        assert cart_item4

        selected_cart_items = [cart_item1, cart_item3]
        cart.checkout_specific_items_in_cart(selected_cart_items)

        assert Cart.objects.count() == 1
        assert CartItem.objects.count() == 4
        assert Order.objects.count() == 1
        assert InstantOrderItem.objects.count() == 1
        assert InstallmentsOrderItem.objects.count() == 1

    def test_checkout_selected_and_order_now_specific_items_in_cart(self):
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
            ItemModel, brand=brand, item_type=item_type, model_name='GE731K-B/SUT',
            enterprise=enterprise_code)
        item_model2 = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731L-C/SUT',
            enterprise=enterprise_code)
        item_model3 = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731M-D/SUT',
            enterprise=enterprise_code)
        item_model4 = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731N-E/SUT',
            enterprise=enterprise_code)
        item1 = baker.make(
            Item, item_model=item_model1, barcode='838383885673', make_year=2020,
            enterprise=enterprise_code)
        item2 = baker.make(
            Item, item_model=item_model2, barcode='838380987383', make_year=2020,
            enterprise=enterprise_code)
        item3 = baker.make(
            Item, item_model=item_model3, barcode='678838383883', make_year=2020,
            enterprise=enterprise_code)
        item4 = baker.make(
            Item, item_model=item_model4, barcode='838383887654', make_year=2020,
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
        baker.make(
            ItemUnits, item=item3, sales_units=s_units, purchases_units=p_units,
            quantity_of_sale_units_per_purchase_unit=12, enterprise=enterprise_code)
        baker.make(
            ItemUnits, item=item4, sales_units=s_units, purchases_units=p_units,
            quantity_of_sale_units_per_purchase_unit=12, enterprise=enterprise_code)
        master_inventory = baker.make(
            Inventory, inventory_name='Elites Working Inventory', is_master=True,
            inventory_type='WORKING STOCK', enterprise=enterprise_code)
        available_inventory = baker.make(
            Inventory, inventory_name='Available Inventory', is_master=False,
            inventory_type='AVAILABLE', enterprise=enterprise_code)
        inventory_item1 = baker.make(InventoryItem, item=item1, enterprise=enterprise_code)
        inventory_item2 = baker.make(InventoryItem, item=item2, enterprise=enterprise_code)
        inventory_item3 = baker.make(InventoryItem, item=item3, enterprise=enterprise_code)
        inventory_item4 = baker.make(InventoryItem, item=item4, enterprise=enterprise_code)

        baker.make(
            InventoryInventoryItem, inventory=master_inventory, inventory_item=inventory_item1)
        baker.make(
            InventoryInventoryItem, inventory=master_inventory, inventory_item=inventory_item2)
        baker.make(
            InventoryInventoryItem, inventory=master_inventory, inventory_item=inventory_item3)
        baker.make(
            InventoryInventoryItem, inventory=master_inventory, inventory_item=inventory_item4)

        baker.make(
            InventoryInventoryItem, inventory=available_inventory, inventory_item=inventory_item1)
        baker.make(
            InventoryInventoryItem, inventory=available_inventory, inventory_item=inventory_item2)
        baker.make(
            InventoryInventoryItem, inventory=available_inventory, inventory_item=inventory_item3)
        baker.make(
            InventoryInventoryItem, inventory=available_inventory, inventory_item=inventory_item4)
        baker.make(
            InventoryRecord, inventory=available_inventory, inventory_item=inventory_item1,
            record_type='ADD', quantity_recorded=20, unit_price=350, enterprise=enterprise_code)
        baker.make(
            InventoryRecord, inventory=available_inventory, inventory_item=inventory_item2,
            record_type='ADD', quantity_recorded=10, unit_price=1000, enterprise=enterprise_code)
        baker.make(
            InventoryRecord, inventory=available_inventory, inventory_item=inventory_item3,
            record_type='ADD', quantity_recorded=5, unit_price=2750, enterprise=enterprise_code)
        baker.make(
            InventoryRecord, inventory=available_inventory, inventory_item=inventory_item4,
            record_type='ADD', quantity_recorded=5, unit_price=2750, enterprise=enterprise_code)
        catalog_item1 = baker.make(
            CatalogItem, inventory_item=inventory_item1, enterprise=enterprise_code)
        catalog_item2 = baker.make(
            CatalogItem, inventory_item=inventory_item2, enterprise=enterprise_code)
        catalog_item3 = baker.make(
            CatalogItem, inventory_item=inventory_item3, enterprise=enterprise_code)
        catalog_item4 = baker.make(
            CatalogItem, inventory_item=inventory_item4, enterprise=enterprise_code)
        customer = baker.make(
            Customer, customer_number=9876, first_name='John', last_name='Wick',
            phone_no='+254712345678', email='johnwick@parabellum.com')
        cart = baker.make(
            Cart, cart_code='EAS-C-10001', customer=customer, enterprise=enterprise_code)
        cart_item1 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item1, quantity_added=3,
            enterprise=enterprise_code)
        cart_item2 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item2, quantity_added=1, order_now=True,
            enterprise=enterprise_code)
        cart_item3 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item3, quantity_added=3,
            is_installment=True, enterprise=enterprise_code)
        cart_item4 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item4, quantity_added=3,
            is_installment=True, enterprise=enterprise_code)

        assert cart_item1
        assert cart_item2
        assert cart_item3
        assert cart_item4

        selected_cart_items = [cart_item1, cart_item3]
        cart.checkout_specific_items_in_cart(selected_cart_items)

        assert Cart.objects.count() == 1
        assert CartItem.objects.count() == 4
        assert Order.objects.count() == 1
        assert InstantOrderItem.objects.count() == 2
        assert InstallmentsOrderItem.objects.count() == 1


class TestCartItem(TestCase):
    """."""

    def test_add_item_to_cart(self):
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
            Inventory, inventory_name='Elites Working Inventory', is_master=True,
            inventory_type='WORKING STOCK', enterprise=enterprise_code)
        available_inventory = baker.make(
            Inventory, inventory_name='Available Inventory', is_master=False,
            inventory_type='AVAILABLE', enterprise=enterprise_code)
        inventory_item = baker.make(InventoryItem, item=item, enterprise=enterprise_code)
        baker.make(
            InventoryInventoryItem, inventory=master_inventory, inventory_item=inventory_item)
        baker.make(
            InventoryInventoryItem, inventory=available_inventory, inventory_item=inventory_item)
        baker.make(
            InventoryRecord, inventory=available_inventory, inventory_item=inventory_item,
            record_type='ADD', quantity_recorded=15, unit_price=350, enterprise=enterprise_code)
        catalog_item = baker.make(
            CatalogItem, inventory_item=inventory_item, enterprise=enterprise_code)
        customer = baker.make(
            Customer, customer_number=9876, first_name='John', last_name='Wick',
            phone_no='+254712345678', email='johnwick@parabellum.com')
        cart = baker.make(
            Cart, cart_code='EAS-C-10001', customer=customer, enterprise=enterprise_code)
        cart_item = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item, quantity_added=2,
            enterprise=enterprise_code)

        assert cart_item
        assert Cart.objects.count() == 1
        assert CartItem.objects.count() == 1

        assert cart.summary == {
            'items': [
                {
                    'index': 0,
                    'name': 'Samsung GE731K-B SUT Cooker',
                    'quantity': 2,
                    'price': 350.0,
                    'total': 700.0}
                ],
            'grand_total': 700.0
            }

    def test_add_similar_item_multiple_times(self):
        """Adding a similar item multiple times."""
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
            Inventory, inventory_name='Elites Working Inventory', is_master=True,
            inventory_type='WORKING STOCK', enterprise=enterprise_code)
        available_inventory = baker.make(
            Inventory, inventory_name='Available Inventory', is_master=False,
            inventory_type='AVAILABLE', enterprise=enterprise_code)
        inventory_item = baker.make(InventoryItem, item=item, enterprise=enterprise_code)
        baker.make(
            InventoryInventoryItem, inventory=master_inventory, inventory_item=inventory_item)
        baker.make(
            InventoryInventoryItem, inventory=available_inventory, inventory_item=inventory_item)
        baker.make(
            InventoryRecord, inventory=available_inventory, inventory_item=inventory_item,
            record_type='ADD', quantity_recorded=20, unit_price=350, enterprise=enterprise_code)
        catalog_item = baker.make(
            CatalogItem, inventory_item=inventory_item, discount_amount=40, quantity=10,
            selling_price=310, enterprise=enterprise_code)
        customer = baker.make(
            Customer, customer_number=9876, first_name='John', last_name='Wick',
            other_names='Baba Yaga', phone_no='+254712345678', email='johnwick@parabellum.com')
        cart = baker.make(
            Cart, cart_code='EAS-C-10001', customer=customer, enterprise=enterprise_code)
        cart_item1 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item, quantity_added=2,
            enterprise=enterprise_code)
        cart_item2 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item, quantity_added=1,
            enterprise=enterprise_code)
        cart_item3 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item, quantity_added=4,
            enterprise=enterprise_code)

        assert cart
        assert cart_item1.opening_quantity == 0
        assert cart_item1.closing_quantity == 2

        assert cart_item2.opening_quantity == 2
        assert cart_item2.closing_quantity == 3

        assert cart_item3.opening_quantity == 3
        assert cart_item3.closing_quantity == 7

        assert cart.summary == {
            'items': [
                {
                    'index': 0,
                    'name': 'Samsung GE731K-B SUT Cooker',
                    'quantity': 7.0,
                    'price': 310.0,
                    'total': 2170.0
                }],
            'grand_total': 2170.0}

    def test_complete_order_for_single_cart_item(self):
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
            ItemModel, brand=brand, item_type=item_type, model_name='RT26HAR2DSA',
            enterprise=enterprise_code)
        item_model2 = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='HSHHSHS8837',
            enterprise=enterprise_code)
        item1 = baker.make(
            Item, item_model=item_model1, barcode='9876543', make_year=2020,
            enterprise=enterprise_code)
        item2 = baker.make(
            Item, item_model=item_model2, barcode='23456789', make_year=2020,
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
            Inventory, inventory_name='Elites Working Inventory', is_master=True,
            inventory_type='WORKING STOCK', enterprise=enterprise_code)
        available_inventory = baker.make(
            Inventory, inventory_name='Available Inventory', is_master=False,
            inventory_type='AVAILABLE', enterprise=enterprise_code)
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
            record_type='ADD', quantity_recorded=15, unit_price=300, enterprise=enterprise_code)
        baker.make(
            InventoryRecord, inventory=available_inventory, inventory_item=inventory_item2,
            record_type='ADD', quantity_recorded=10, unit_price=300, enterprise=enterprise_code)
        catalog_item1 = baker.make(
            CatalogItem, inventory_item=inventory_item1, enterprise=enterprise_code)
        baker.make(
            CatalogItem, inventory_item=inventory_item2, enterprise=enterprise_code)
        customer = baker.make(
            Customer, customer_number=9876, first_name='John', last_name='Wick',
            other_names='Baba Yaga', phone_no='+254712345678', email='johnwick@parabellum.com')
        cart = baker.make(Cart, customer=customer)
        cart_item1 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item1, quantity_added=2,
            order_now=True, enterprise=enterprise_code)
        cart_item2 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item1, quantity_added=1,
            order_now=True, is_installment=True, enterprise=enterprise_code)

        assert cart_item1
        assert cart_item2
        cart_item1.checkout_cart_item()
        cart_item2.checkout_cart_item()

        assert Cart.objects.count() == 1
        assert CartItem.objects.count() == 2
        assert Order.objects.count() == 2
        assert InstantOrderItem.objects.count() == 1
        assert InstallmentsOrderItem.objects.count() == 1
