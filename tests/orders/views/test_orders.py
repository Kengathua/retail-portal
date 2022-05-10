"""Tests for order views file."""

import datetime
from rest_framework.test import APITestCase

from elites_franchise_portal.items.models import (
    Brand, BrandItemType, Category, Item, ItemModel, ItemType,
    ItemUnits, UnitsItemType, Units)
from elites_franchise_portal.debit.models import (
    InventoryItem, InventoryRecord, Sale, SaleRecord)
from elites_franchise_portal.franchises.models import Franchise
from elites_franchise_portal.catalog.models import CatalogItem
from elites_franchise_portal.orders.models import (
    Cart, CartItem, Order, InstantOrderItem, InstallmentsOrderItem, Installment)
from elites_franchise_portal.customers.models import Customer


from tests.utils import APITests

from model_bakery import baker
from model_bakery.recipe import Recipe


class TestOrderView(APITests, APITestCase):
    """."""

    def setUp(self):
        """."""
        franchise = baker.make(
            Franchise, reg_no='BS-9049444', name='Franchise One',
            elites_code='EAL-F/FO-MB/2201-01', partnership_type='SHOP')
        franchise_code = franchise.elites_code
        customer = baker.make(
            Customer, customer_number=9876, first_name='John',
            last_name='Wick', other_names='Baba Yaga',
            phone_no='+254712345678', email='johnwick@parabellum.com', franchise=franchise_code)
        cart = baker.make(
            Cart, cart_code='EAS-C-10001', customer=customer, franchise=franchise_code)
        self.recipe = Recipe(
            Order, customer=customer, cart_code=cart.cart_code, franchise=franchise_code)

    url = 'v1:orders:order'


class TestInstantOrderItemView(APITests, APITestCase):
    """."""

    def setUp(self):
        """."""
        franchise = baker.make(
            Franchise, reg_no='BS-9049444', name='Franchise One',
            elites_code='EAL-F/FO-MB/2201-01', partnership_type='SHOP')
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
        inventory_item = baker.make(
            InventoryItem, item=item, franchise=franchise_code)
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
        self.recipe = Recipe(
            InstantOrderItem, order=order, franchise=franchise.elites_code,
            cart_item=cart_item, confirmation_status='CONFIRMED', amount_paid=350)

    url = 'v1:orders:instantorderitem'


class TestInstallmentOrderItemView(APITests, APITestCase):
    """."""

    def setUp(self):
        """."""
        franchise = baker.make(
            Franchise, reg_no='BS-9049444', name='Franchise One',
            elites_code='EAL-F/FO-MB/2201-01', partnership_type='SHOP')
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
        inventory_item = baker.make(
            InventoryItem, item=item, franchise=franchise_code)
        baker.make(
            InventoryRecord, inventory_item=inventory_item, record_type='ADD',
            quantity_recorded=20, unit_price=350, franchise=franchise_code)
        catalog_item = baker.make(
            CatalogItem, inventory_item=inventory_item, franchise=franchise_code)
        customer = baker.make(
            Customer, title='Mr', customer_number=9876, first_name='John',
            last_name='Wick', other_names='Baba Yaga', gender='MALE',
            phone_no='+254712345678', email='johnwick@parabellum.com')
        cart = baker.make(
            Cart, cart_code='EAS-C-10001', customer=customer, franchise=franchise_code)
        cart_item = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item, quantity_added=2,
            franchise=franchise_code)
        order = baker.make(Order, customer=customer, franchise=franchise_code)
        self.recipe = Recipe(
            InstallmentsOrderItem, franchise=franchise.elites_code,
            order=order, cart_item=cart_item,  confirmation_status='CONFIRMED',
            amount_paid=150, deposit_amount=150)

    url = 'v1:orders:installmentorderitem'


class TestInstallmentView(APITests, APITestCase):
    """."""

    def setUp(self):
        """."""
        franchise = baker.make(
            Franchise, reg_no='BS-9049444', name='Franchise One',
            elites_code='EAL-F/FO-MB/2201-01', partnership_type='SHOP')
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
        inventory_item = baker.make(
            InventoryItem, item=item, franchise=franchise_code)
        baker.make(
            InventoryRecord, inventory_item=inventory_item, record_type='ADD',
            quantity_recorded=20, unit_price=350, franchise=franchise_code)
        catalog_item = baker.make(
            CatalogItem, inventory_item=inventory_item, franchise=franchise_code)
        customer = baker.make(
            Customer, title='Mr', customer_number=9876, first_name='John',
            last_name='Wick', other_names='Baba Yaga', gender='MALE',
            phone_no='+254712345678', email='johnwick@parabellum.com', franchise=franchise_code)
        cart = baker.make(
            Cart, cart_code='EAS-C-10001', customer=customer, franchise=franchise_code)
        cart_item = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item, quantity_added=2,
            franchise=franchise_code)
        order = baker.make(
            Order, customer=customer, cart_code=cart.cart_code, franchise=franchise_code)
        installment_order_item = baker.make(
            InstallmentsOrderItem, franchise=franchise_code,
            order=order, cart_item=cart_item,  confirmation_status='CONFIRMED',
            amount_paid=150, deposit_amount=150)
        next_installment_date = datetime.date.today() + datetime.timedelta(30)
        self.recipe = Recipe(
            Installment, installment_item=installment_order_item, amount=100,
            next_installment_date=next_installment_date,
            franchise=franchise_code)

    url = 'v1:orders:installment'
