import pytest
from rest_framework.test import APITestCase

from tests.utils.api import APITests
from elites_franchise_portal.franchises.models import Franchise
from elites_franchise_portal.items.models import (
    Brand, BrandItemType, Category, Item, ItemModel, ItemType,
    ItemUnits, UnitsItemType, Units)
from elites_franchise_portal.debit.models import (
    InventoryItem, InventoryRecord, Store, StoreRecord)

from tests.utils.login_mixins import LoggedInMixin, authenticate_test_user

from model_bakery import baker
from model_bakery.recipe import Recipe, foreign_key

pytestmark = pytest.mark.django_db


class TestStoreView(APITests, APITestCase):

    def setUp(self):
        franchise = baker.make(
            Franchise, name='Franchise One', partnership_type='SHOP')
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
        self.recipe = Recipe(Store, item=item, franchise=franchise_code)

    url = 'v1:debit:store'


class TestStoreRecordView(APITests, APITestCase):

    def setUp(self):
        franchise = baker.make(
            Franchise, name='Franchise One', partnership_type='SHOP')
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
        store = baker.make(
            Store, item=item, franchise=franchise_code)
        self.recipe = Recipe(
            StoreRecord, store=store, record_type='ADD',
            quantity_recorded=15, unit_price=300, franchise=franchise_code)

    url = 'v1:debit:storerecord'


class TestInventoryItemView(APITests, APITestCase):

    def setUp(self):
        franchise = baker.make(
            Franchise, name='Franchise One', partnership_type='SHOP')
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
        self.recipe = Recipe(InventoryItem, item=item, franchise=franchise_code)

    url = 'v1:debit:inventoryitem'


class TestInventoryRecordView(APITests, APITestCase):

    def setUp(self):
        franchise = baker.make(
            Franchise, name='Franchise One', partnership_type='SHOP')
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
        inventoy_item = baker.make(
            InventoryItem, item=item, franchise=franchise_code)
        self.recipe = Recipe(
            InventoryRecord, inventory_item=inventoy_item, record_type='ADD',
            quantity_recorded=15, unit_price=300, franchise=franchise_code)

    url = 'v1:debit:inventoryrecord'
