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
    InventoryItem, InventoryRecord, Sale, SaleRecord,
    Store, StoreRecord)
from elites_franchise_portal.catalog.models import CatalogItem
from elites_franchise_portal.orders.models import (
    Cart, CartItem, Order, InstantOrderItem, InstallmentsOrderItem)
from elites_franchise_portal.franchises.models import Franchise
from elites_franchise_portal.customers.models import Customer

from model_bakery import baker


class TestCart(TestCase):
    """."""

    def test_create_cart(self):
        """."""
        franchise = baker.make(Franchise, name='Elites Age Supermarket')
        franchise_code = franchise.elites_code
        customer = baker.make(
            Customer, customer_number=9876, first_name='John', last_name='Wick',
            phone_no='+254712345678', email='johnwick@parabellum.com', franchise=franchise_code)
        cart = baker.make(
            Cart, customer=customer, cart_code='EAS-C-10001', franchise=franchise_code)

        assert cart
        assert Cart.objects.count() == 1

    def test_fail_checkout_empty_cart(self):
        """."""
        franchise = baker.make(Franchise, name='Elites Age Supermarket')
        franchise_code = franchise.elites_code
        customer = baker.make(
            Customer, customer_number=9876, first_name='John', last_name='Wick',
            phone_no='+254712345678', email='johnwick@parabellum.com', franchise=franchise_code)
        cart = baker.make(
            Cart, customer=customer, cart_code='EAS-C-10001', franchise=franchise_code)

        with pytest.raises(ValidationError) as ve:
            cart.checkout_cart()
        msg = 'Cart is empty. Please add items to checkout'
        assert msg in ve.value.messages

    def test_check_if_site_cart(self):
        """."""
        franchise = baker.make(Franchise, name='Elites Age Supermarket')
        franchise_code = franchise.elites_code
        test_user = get_user_model().objects.create_superuser(
            email='testuser@email.com', first_name='Test', last_name='User',
            guid=uuid.uuid4(), password='Testpass254$', franchise=franchise_code)
        customer = baker.make(
            Customer, customer_number=9876, first_name='John', last_name='Wick',
            is_franchise=True, franchise_user=test_user, phone_no='+254712345678',
            email='johnwick@parabellum.com', franchise=franchise_code)
        cart = baker.make(
            Cart, cart_code='EAS-C-10001', customer=customer, franchise=franchise_code)

        assert cart
        assert cart.is_franchise == True # noqa
        assert Cart.objects.count() == 1    # noqa

    def test_checkout_cart_instant_order_item(self):
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
            ItemModel, brand_item_type=brand_item_type, model_name='GE731K-B/SUT',
            franchise=franchise_code)
        item_model2 = baker.make(
            ItemModel, brand_item_type=brand_item_type, model_name='GE731L-C/SUT',
            franchise=franchise_code)
        item_model3 = baker.make(
            ItemModel, brand_item_type=brand_item_type, model_name='GE731M-D/SUT',
            franchise=franchise_code)
        item_model4 = baker.make(
            ItemModel, brand_item_type=brand_item_type, model_name='GE731N-E/SUT',
            franchise=franchise_code)
        item1 = baker.make(
            Item, item_model=item_model1, barcode='838383885673', make_year=2020,
            create_inventory_item=False, franchise=franchise_code)
        item2 = baker.make(
            Item, item_model=item_model2, barcode='838380987383', make_year=2020,
            create_inventory_item=False, franchise=franchise_code)
        item3 = baker.make(
            Item, item_model=item_model3, barcode='678838383883', make_year=2020,
            create_inventory_item=False, franchise=franchise_code)
        item4 = baker.make(
            Item, item_model=item_model4, barcode='838383887654', make_year=2020,
            create_inventory_item=False, franchise=franchise_code)
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
        inventory_item1 = baker.make(
            InventoryItem, item=item1, description=item1.item_name, franchise=franchise_code)
        inventory_item2 = baker.make(
            InventoryItem, item=item2, description=item2.item_name, franchise=franchise_code)
        inventory_item3 = baker.make(
            InventoryItem, item=item3, description=item3.item_name, franchise=franchise_code)
        inventory_item4 = baker.make(
            InventoryItem, item=item4, description=item3.item_name, franchise=franchise_code)
        baker.make(
            InventoryRecord, inventory_item=inventory_item1, record_type='ADD',
            quantity_recorded=20, unit_price=350,
            franchise=franchise_code)
        baker.make(
            InventoryRecord, inventory_item=inventory_item2, record_type='ADD',
            quantity_recorded=10, unit_price=1000,
            franchise=franchise_code)
        baker.make(
            InventoryRecord, inventory_item=inventory_item3, record_type='ADD',
            quantity_recorded=5, unit_price=2750,
            franchise=franchise_code)
        baker.make(
            InventoryRecord, inventory_item=inventory_item4, record_type='ADD',
            quantity_recorded=5, unit_price=2750,
            franchise=franchise_code)
        catalog_item1 = baker.make(
            CatalogItem, inventory_item=inventory_item1, franchise=franchise_code)
        catalog_item2 = baker.make(
            CatalogItem, inventory_item=inventory_item2, franchise=franchise_code)
        catalog_item3 = baker.make(
            CatalogItem, inventory_item=inventory_item3, franchise=franchise_code)
        catalog_item4 = baker.make(
            CatalogItem, inventory_item=inventory_item4, franchise=franchise_code)
        customer = baker.make(
            Customer, customer_number=9876, first_name='John', last_name='Wick',
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
            CartItem, cart=cart, catalog_item=catalog_item3, quantity_added=3, is_installment=True,
            franchise=franchise_code)
        cart_item4 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item4, quantity_added=3, is_installment=True,
            franchise=franchise_code)
        cart.checkout_cart()

        assert cart_item1
        assert cart_item2
        assert cart_item3
        assert cart_item4
        assert Order.objects.count() == 1
        assert InstantOrderItem.objects.count() == 2
        assert InstallmentsOrderItem.objects.count() == 2

        order = Order.objects.get(customer=customer)
        customer.is_franchise = True
        customer.save()
        cart.customer = customer
        cart.save()
        assert order.is_franchise == False   # noqa
        cart.checkout_cart()
        order.refresh_from_db()
        assert order.is_franchise == True    # noqa

    def test_fail_checkout_specific_items_empyt_cart(self):
        """."""
        franchise = baker.make(Franchise, name='Elites Age Supermarket')
        franchise_code = franchise.elites_code
        customer = baker.make(
            Customer, customer_number=9876, first_name='John', last_name='Wick',
            phone_no='+254712345678', email='johnwick@parabellum.com',
            franchise=franchise_code)
        cart = baker.make(
            Cart, customer=customer, cart_code='EAS-C-10001', franchise=franchise_code)

        with pytest.raises(ValidationError) as ve:
            cart.checkout_specific_items_in_cart([])
        msg = 'Fast checkout cart is empty. Please add items to checkout'
        assert msg in ve.value.messages

    def test_checkout_specific_order_now_items_in_cart(self):
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
            ItemModel, brand_item_type=brand_item_type, model_name='GE731K-B/SUT',
            franchise=franchise_code)
        item_model2 = baker.make(
            ItemModel, brand_item_type=brand_item_type, model_name='GE731L-C/SUT',
            franchise=franchise_code)
        item_model3 = baker.make(
            ItemModel, brand_item_type=brand_item_type, model_name='GE731M-D/SUT',
            franchise=franchise_code)
        item_model4 = baker.make(
            ItemModel, brand_item_type=brand_item_type, model_name='GE731N-E/SUT',
            franchise=franchise_code)
        item1 = baker.make(
            Item, item_model=item_model1, barcode='838383885673', make_year=2020,
            create_inventory_item=False, franchise=franchise_code)
        item2 = baker.make(
            Item, item_model=item_model2, barcode='838380987383', make_year=2020,
            create_inventory_item=False, franchise=franchise_code)
        item3 = baker.make(
            Item, item_model=item_model3, barcode='678838383883', make_year=2020,
            create_inventory_item=False, franchise=franchise_code)
        item4 = baker.make(
            Item, item_model=item_model4, barcode='838383887654', make_year=2020,
            create_inventory_item=False, franchise=franchise_code)
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
        inventory_item1 = baker.make(
            InventoryItem, item=item1, description=item1.item_name, franchise=franchise_code)
        inventory_item2 = baker.make(
            InventoryItem, item=item2, description=item2.item_name, franchise=franchise_code)
        inventory_item3 = baker.make(
            InventoryItem, item=item3, description=item3.item_name, franchise=franchise_code)
        inventory_item4 = baker.make(
            InventoryItem, item=item4, description=item3.item_name, franchise=franchise_code)
        baker.make(
            InventoryRecord, inventory_item=inventory_item1, record_type='ADD',
            quantity_recorded=20, unit_price=350,
            franchise=franchise_code)
        baker.make(
            InventoryRecord, inventory_item=inventory_item2, record_type='ADD',
            quantity_recorded=10, unit_price=1000,
            franchise=franchise_code)
        baker.make(
            InventoryRecord, inventory_item=inventory_item3, record_type='ADD',
            quantity_recorded=5, unit_price=2750,
            franchise=franchise_code)
        baker.make(
            InventoryRecord, inventory_item=inventory_item4, record_type='ADD',
            quantity_recorded=5, unit_price=2750,
            franchise=franchise_code)
        catalog_item1 = baker.make(
            CatalogItem, inventory_item=inventory_item1, franchise=franchise_code)
        catalog_item2 = baker.make(
            CatalogItem, inventory_item=inventory_item2, franchise=franchise_code)
        catalog_item3 = baker.make(
            CatalogItem, inventory_item=inventory_item3, franchise=franchise_code)
        catalog_item4 = baker.make(
            CatalogItem, inventory_item=inventory_item4, franchise=franchise_code)
        customer = baker.make(
            Customer, customer_number=9876, first_name='John', last_name='Wick',
            phone_no='+254712345678', email='johnwick@parabellum.com')
        cart = baker.make(
            Cart, cart_code='EAS-C-10001', customer=customer, franchise=franchise_code)
        cart_item1 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item1, quantity_added=3, order_now=True,
            franchise=franchise_code)
        cart_item2 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item2, quantity_added=1,
            franchise=franchise_code)
        cart_item3 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item3, quantity_added=3, is_installment=True,
            order_now=True, franchise=franchise_code)
        cart_item4 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item4, quantity_added=3, is_installment=True,
            franchise=franchise_code)

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
        customer.is_franchise = True
        customer.save()
        cart.customer = customer
        cart.save()
        assert order.is_franchise == False   # noqa
        cart.checkout_cart()
        order.refresh_from_db()
        assert order.is_franchise == True    # noqa

    def test_checkout_selected_specific_items_in_cart(self):
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
            ItemModel, brand_item_type=brand_item_type, model_name='GE731K-B/SUT',
            franchise=franchise_code)
        item_model2 = baker.make(
            ItemModel, brand_item_type=brand_item_type, model_name='GE731L-C/SUT',
            franchise=franchise_code)
        item_model3 = baker.make(
            ItemModel, brand_item_type=brand_item_type, model_name='GE731M-D/SUT',
            franchise=franchise_code)
        item_model4 = baker.make(
            ItemModel, brand_item_type=brand_item_type, model_name='GE731N-E/SUT',
            franchise=franchise_code)
        item1 = baker.make(
            Item, item_model=item_model1, barcode='838383885673', make_year=2020,
            create_inventory_item=False, franchise=franchise_code)
        item2 = baker.make(
            Item, item_model=item_model2, barcode='838380987383', make_year=2020,
            create_inventory_item=False, franchise=franchise_code)
        item3 = baker.make(
            Item, item_model=item_model3, barcode='678838383883', make_year=2020,
            create_inventory_item=False, franchise=franchise_code)
        item4 = baker.make(
            Item, item_model=item_model4, barcode='838383887654', make_year=2020,
            create_inventory_item=False, franchise=franchise_code)
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
        inventory_item1 = baker.make(
            InventoryItem, item=item1, description=item1.item_name, franchise=franchise_code)
        inventory_item2 = baker.make(
            InventoryItem, item=item2, description=item2.item_name, franchise=franchise_code)
        inventory_item3 = baker.make(
            InventoryItem, item=item3, description=item3.item_name, franchise=franchise_code)
        inventory_item4 = baker.make(
            InventoryItem, item=item4, description=item3.item_name, franchise=franchise_code)
        baker.make(
            InventoryRecord, inventory_item=inventory_item1, record_type='ADD',
            quantity_recorded=20, unit_price=350,
            franchise=franchise_code)
        baker.make(
            InventoryRecord, inventory_item=inventory_item2, record_type='ADD',
            quantity_recorded=10, unit_price=1000,
            franchise=franchise_code)
        baker.make(
            InventoryRecord, inventory_item=inventory_item3, record_type='ADD',
            quantity_recorded=5, unit_price=2750,
            franchise=franchise_code)
        baker.make(
            InventoryRecord, inventory_item=inventory_item4, record_type='ADD',
            quantity_recorded=5, unit_price=2750,
            franchise=franchise_code)
        catalog_item1 = baker.make(
            CatalogItem, inventory_item=inventory_item1, franchise=franchise_code)
        catalog_item2 = baker.make(
            CatalogItem, inventory_item=inventory_item2, franchise=franchise_code)
        catalog_item3 = baker.make(
            CatalogItem, inventory_item=inventory_item3, franchise=franchise_code)
        catalog_item4 = baker.make(
            CatalogItem, inventory_item=inventory_item4, franchise=franchise_code)
        customer = baker.make(
            Customer, customer_number=9876, first_name='John', last_name='Wick',
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
            is_installment=True, franchise=franchise_code)
        cart_item4 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item4, quantity_added=3,
            is_installment=True, franchise=franchise_code)

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
            ItemModel, brand_item_type=brand_item_type, model_name='GE731K-B/SUT',
            franchise=franchise_code)
        item_model2 = baker.make(
            ItemModel, brand_item_type=brand_item_type, model_name='GE731L-C/SUT',
            franchise=franchise_code)
        item_model3 = baker.make(
            ItemModel, brand_item_type=brand_item_type, model_name='GE731M-D/SUT',
            franchise=franchise_code)
        item_model4 = baker.make(
            ItemModel, brand_item_type=brand_item_type, model_name='GE731N-E/SUT',
            franchise=franchise_code)
        item1 = baker.make(
            Item, item_model=item_model1, barcode='838383885673', make_year=2020,
            create_inventory_item=False, franchise=franchise_code)
        item2 = baker.make(
            Item, item_model=item_model2, barcode='838380987383', make_year=2020,
            create_inventory_item=False, franchise=franchise_code)
        item3 = baker.make(
            Item, item_model=item_model3, barcode='678838383883', make_year=2020,
            create_inventory_item=False, franchise=franchise_code)
        item4 = baker.make(
            Item, item_model=item_model4, barcode='838383887654', make_year=2020,
            create_inventory_item=False, franchise=franchise_code)
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
        inventory_item1 = baker.make(
            InventoryItem, item=item1, description=item1.item_name, franchise=franchise_code)
        inventory_item2 = baker.make(
            InventoryItem, item=item2, description=item2.item_name, franchise=franchise_code)
        inventory_item3 = baker.make(
            InventoryItem, item=item3, description=item3.item_name, franchise=franchise_code)
        inventory_item4 = baker.make(
            InventoryItem, item=item4, description=item3.item_name, franchise=franchise_code)
        baker.make(
            InventoryRecord, inventory_item=inventory_item1, record_type='ADD',
            quantity_recorded=20, unit_price=350,
            franchise=franchise_code)
        baker.make(
            InventoryRecord, inventory_item=inventory_item2, record_type='ADD',
            quantity_recorded=10, unit_price=1000,
            franchise=franchise_code)
        baker.make(
            InventoryRecord, inventory_item=inventory_item3, record_type='ADD',
            quantity_recorded=5, unit_price=2750,
            franchise=franchise_code)
        baker.make(
            InventoryRecord, inventory_item=inventory_item4, record_type='ADD',
            quantity_recorded=5, unit_price=2750,
            franchise=franchise_code)
        catalog_item1 = baker.make(
            CatalogItem, inventory_item=inventory_item1, franchise=franchise_code)
        catalog_item2 = baker.make(
            CatalogItem, inventory_item=inventory_item2, franchise=franchise_code)
        catalog_item3 = baker.make(
            CatalogItem, inventory_item=inventory_item3, franchise=franchise_code)
        catalog_item4 = baker.make(
            CatalogItem, inventory_item=inventory_item4, franchise=franchise_code)
        customer = baker.make(
            Customer, customer_number=9876, first_name='John', last_name='Wick',
            phone_no='+254712345678', email='johnwick@parabellum.com')
        cart = baker.make(
            Cart, cart_code='EAS-C-10001', customer=customer, franchise=franchise_code)
        cart_item1 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item1, quantity_added=3,
            franchise=franchise_code)
        cart_item2 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item2, quantity_added=1, order_now=True,
            franchise=franchise_code)
        cart_item3 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item3, quantity_added=3,
            is_installment=True, franchise=franchise_code)
        cart_item4 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item4, quantity_added=3,
            is_installment=True, franchise=franchise_code)

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
            ItemModel, brand_item_type=brand_item_type, model_name='GE731K-B SUT',
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
        inventory_item = baker.make(
            InventoryItem, item=item, franchise=franchise_code)
        baker.make(
            InventoryRecord, inventory_item=inventory_item, record_type='ADD',
            quantity_recorded=15, unit_price=350, franchise=franchise_code)
        catalog_item = baker.make(
            CatalogItem, inventory_item=inventory_item, franchise=franchise_code)
        customer = baker.make(
            Customer, customer_number=9876, first_name='John', last_name='Wick',
            phone_no='+254712345678', email='johnwick@parabellum.com')
        cart = baker.make(
            Cart, cart_code='EAS-C-10001', customer=customer, franchise=franchise_code)
        cart_item = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item, quantity_added=2,
            franchise=franchise_code)

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
            ItemModel, brand_item_type=brand_item_type, model_name='GE731K-B SUT',
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
        inventory_item = baker.make(
            InventoryItem, item=item, franchise=franchise_code)
        baker.make(
            InventoryRecord, inventory_item=inventory_item, record_type='ADD',
            quantity_recorded=20, unit_price=350,
            franchise=franchise_code)
        catalog_item = baker.make(
            CatalogItem, inventory_item=inventory_item, discount_amount=40, quantity=10,
            selling_price=310, franchise=franchise_code)
        customer = baker.make(
            Customer, customer_number=9876, first_name='John', last_name='Wick',
            other_names='Baba Yaga', phone_no='+254712345678', email='johnwick@parabellum.com')
        cart = baker.make(
            Cart, cart_code='EAS-C-10001', customer=customer, franchise=franchise_code)
        cart_item1 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item, quantity_added=2,
            franchise=franchise_code)
        cart_item2 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item, quantity_added=1,
            franchise=franchise_code)
        cart_item3 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item, quantity_added=4,
            franchise=franchise_code)

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
            ItemModel, brand_item_type=brand_item_type, model_name='RT26HAR2DSA',
            franchise=franchise_code)
        item_model2 = baker.make(
            ItemModel, brand_item_type=brand_item_type, model_name='HSHHSHS8837',
            franchise=franchise_code)
        item1 = baker.make(
            Item, item_model=item_model1, barcode='9876543', make_year=2020,
            create_inventory_item=False, franchise=franchise_code)
        item2 = baker.make(
            Item, item_model=item_model2, barcode='23456789', make_year=2020,
            create_inventory_item=False, franchise=franchise_code)
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
        inventory_item1 = baker.make(InventoryItem, item=item1, franchise=franchise_code)
        inventory_item2 = baker.make(InventoryItem, item=item2, franchise=franchise_code)
        baker.make(
            InventoryRecord, inventory_item=inventory_item1, record_type='ADD',
            quantity_recorded=15, unit_price=300, franchise=franchise_code)
        baker.make(
            InventoryRecord, inventory_item=inventory_item2, record_type='ADD',
            quantity_recorded=10, unit_price=300, franchise=franchise_code)
        catalog_item1 = baker.make(
            CatalogItem, inventory_item=inventory_item1, franchise=franchise_code)
        baker.make(
            CatalogItem, inventory_item=inventory_item2, franchise=franchise_code)
        customer = baker.make(
            Customer, customer_number=9876, first_name='John', last_name='Wick',
            other_names='Baba Yaga', phone_no='+254712345678', email='johnwick@parabellum.com')
        cart = baker.make(Cart, customer=customer)
        cart_item1 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item1, quantity_added=2,
            order_now=True, franchise=franchise_code)
        cart_item2 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item1, quantity_added=1,
            order_now=True, is_installment=True, franchise=franchise_code)

        assert cart_item1
        assert cart_item2
        cart_item1.checkout_cart_item()
        cart_item2.checkout_cart_item()

        assert Cart.objects.count() == 1
        assert CartItem.objects.count() == 2
        assert Order.objects.count() == 2
        assert InstantOrderItem.objects.count() == 1
        assert InstallmentsOrderItem.objects.count() == 1
