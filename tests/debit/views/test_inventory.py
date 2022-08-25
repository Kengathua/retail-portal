
import pytest
from rest_framework.test import APITestCase
from django.urls import reverse

from tests.utils.api import APITests
from elites_franchise_portal.franchises.models import Franchise
from elites_franchise_portal.items.models import (
    Brand, BrandItemType, Category, Item, ItemModel, ItemType,)
from elites_franchise_portal.debit.models import (
    Inventory, InventoryItem, InventoryInventoryItem, InventoryRecord,)
from tests.utils.login_mixins import authenticate_test_user

from model_bakery import baker
from model_bakery.recipe import Recipe, foreign_key

pytestmark = pytest.mark.django_db


class InvetoryAPITests(APITests):

    def test_post(self, status_code=201):
        self.client = authenticate_test_user()
        instance = self.make()
        test_data = self.get_test_data(instance)
        url = reverse(self.url + '-list')
        resp = self.client.post(url, test_data)
        assert resp.status_code == status_code, '{}, {}, {}'.format(resp.content, url, test_data)  # noqa
        if resp.status_code != 201:
            return resp

        self.compare_dicts(test_data, resp.data)

        return test_data, resp


    def test_put(self, status_code=200):
        self.client = authenticate_test_user()
        instance = self.make()
        test_id = getattr(instance, self.id_field)
        test_data = self.get_test_data(instance)
        url = reverse(
            self.url + '-detail', kwargs={self.id_field: test_id}
        )

        resp = self.client.put(url, test_data)
        assert resp.status_code == status_code, '{}, {}, {}'.format(resp.content, url, test_data)
        return resp

    def test_patch(self, status_code=200):
        self.client = authenticate_test_user()
        instance = self.make()
        test_data = self.get_test_data(instance)
        test_id = getattr(instance, self.id_field)
        assert test_id, test_id
        assert instance.__class__.objects.get(pk=test_id), \
            'unable to get instance with PK {}'.format(test_id)
        url = reverse(
            self.url + '-detail', kwargs={self.id_field: test_id}
        )
        resp = self.client.patch(url, test_data)
        assert resp.status_code == status_code, '{}, {}, {}'.format(resp.content, url, test_data)
        return resp


class TestInventoryView(APITests, APITestCase):

    def setUp(self):
        franchise = baker.make(
            Franchise, name='Franchise One', partnership_type='SHOP')
        franchise_code = franchise.elites_code
        self.recipe = Recipe(
            Inventory, inventory_name='Elites Age Supermarket Working Stock Inventory',
            inventory_type='WORKING STOCK', franchise=franchise_code)

    url = 'v1:debit:inventory'


class TestInventoryItemView(InvetoryAPITests, APITestCase):

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
        baker.make(
            BrandItemType, brand=brand, item_type=item_type,
            franchise=franchise_code)
        item_model = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731K-B SUT',
            franchise=franchise_code)
        item = baker.make(
            Item, item_model=item_model, barcode='83838388383', make_year=2020,
            franchise=franchise_code)
        inventory_item = InventoryItem.objects.get(item=item, franchise=franchise_code).delete()
        InventoryInventoryItem.objects.filter(inventory_item=inventory_item).delete()
        self.recipe = Recipe(InventoryItem, item=item, description=item.item_name, franchise=franchise_code)

    url = 'v1:debit:inventoryitem'

class TestInventoryInventoryItemView(InvetoryAPITests, APITestCase):

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
        baker.make(
            BrandItemType, brand=brand, item_type=item_type,
            franchise=franchise_code)
        item_model = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731K-B SUT',
            franchise=franchise_code)
        item = baker.make(
            Item, item_model=item_model, barcode='83838388383', make_year=2020,
            franchise=franchise_code)
        inventory = baker.make(
            Inventory, inventory_name='Elites Age Supermarket Working Stock Inventory',
            inventory_type='WORKING STOCK', franchise=franchise_code)
        inventory_item = InventoryItem.objects.get(item=item, franchise=franchise_code)
        self.recipe = Recipe(
            InventoryInventoryItem, inventory=inventory, inventory_item=inventory_item, franchise=franchise_code)

    url = 'v1:debit:inventoryinventoryitem'


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
        baker.make(
            BrandItemType, brand=brand, item_type=item_type,
            franchise=franchise_code)
        item_model = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731K-B SUT',
            franchise=franchise_code)
        item = baker.make(
            Item, item_model=item_model, barcode='83838388383', make_year=2020,
            franchise=franchise_code)
        inventory_item = InventoryItem.objects.get(item=item, franchise=franchise_code)
        self.recipe = Recipe(
            InventoryRecord, inventory_item=inventory_item, record_type='ADD',
            quantity_recorded=15, unit_price=300, franchise=franchise_code)

    url = 'v1:debit:inventoryrecord'

    def test_post(self, status_code=201):
        pass

    def test_put(self, status_code=200):
        pass

    def test_patch(self, status_code=200):
        pass
