"""Catalog views file."""

from tests.utils.api import APITests
from rest_framework.test import APITestCase
from django.db.models import ForeignKey, OneToOneField
from django.urls import reverse

from elites_franchise_portal.items.models import (
    Brand, BrandItemType, Category, Item, ItemModel, ItemType,
    ItemUnits, UnitsItemType, Units)
from elites_franchise_portal.debit.models import (
    InventoryItem, InventoryRecord, Sale, SaleRecord)
from elites_franchise_portal.catalog.models import (
    Section, Catalog, CatalogItem, CatalogCatalogItem)
from elites_franchise_portal.debit.models import (
    Inventory, InventoryItem, InventoryInventoryItem)
from elites_franchise_portal.enterprises.models import Enterprise
from tests.utils.login_mixins import authenticate_test_user

from model_bakery import baker
from model_bakery.recipe import Recipe, foreign_key

class TestSectionView(APITests, APITestCase):
    def setUp(self):
        # using the Setup function helps avoid using recipes for foregn keys
        # or the django db mark error
        franchise = baker.make(
            Enterprise, name='Franchise One', enterprise_code='EAL-F/FO-MB/2201-01',
            business_type='SHOP')
        enterprise_code = franchise.enterprise_code
        self.recipe = Recipe(
            Section, section_name='Section A', enterprise=enterprise_code)

    url = 'v1:catalog:section'


class TestCatalogView(APITests, APITestCase):
    def setUp(self):
        franchise = baker.make(
            Enterprise, name='Franchise One', enterprise_code='EAL-F/FO-MB/2201-01',
            business_type='SHOP')
        enterprise_code = franchise.enterprise_code
        self.recipe = Recipe(
            Catalog, catalog_name='Elites Age Supermarket Standard Catalog',
            description='Standard Catalog', is_standard=True, enterprise=enterprise_code)

    url = 'v1:catalog:catalog'


class TestCatalogItemView(APITests, APITestCase):
    """."""

    def setUp(self):
        """."""
        franchise = baker.make(
            Enterprise, name='Franchise One', enterprise_code='EAL-F/FO-MB/2201-01',
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
        inventory_item = baker.make(InventoryItem, item=item, enterprise=enterprise_code)
        baker.make(
            InventoryInventoryItem, inventory=master_inventory, inventory_item=inventory_item)
        baker.make(
            InventoryInventoryItem, inventory=available_inventory, inventory_item=inventory_item)
        baker.make(
            InventoryRecord, inventory=available_inventory, inventory_item=inventory_item, record_type='ADD',
            quantity_recorded=15, unit_price=300, enterprise=enterprise_code)
        section = baker.make(
            Section, section_name='Section A', enterprise=enterprise_code)
        self.recipe = Recipe(
            CatalogItem, inventory_item=inventory_item, section=section, enterprise=enterprise_code)

    url = 'v1:catalog:catalogitem'

    def test_post(self, status_code=201):
        """."""
        self.client = authenticate_test_user()
        catalog_item = self.make()
        data = self.get_test_data(catalog_item)

        url = reverse(self.url + '-list')
        resp = self.client.post(url, data)
        assert resp.status_code == status_code, '{}, {}, {}'.format(resp.content, url, data)  # noqa
        if resp.status_code != 201:
            return resp
        self.compare_dicts(data, resp.data)

        return data, resp

    def test_patch(self, status_code=200):
        """."""
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

    def test_put(self, status_code=200):
        """."""
        self.client = authenticate_test_user()

        instance = self.make()
        test_data = self.get_test_data(instance)

        test_id = getattr(instance, self.id_field)
        url = reverse(
            self.url + '-detail', kwargs={self.id_field: test_id}
        )

        resp = self.client.put(url, test_data)
        assert resp.status_code == status_code, '{}, {}, {}'.format(resp.content, url, test_data)
        return resp

class TestCatalogCatalogItemView(APITests, APITestCase):
    """."""

    def setUp(self):
        """."""
        franchise = baker.make(
            Enterprise, name='Franchise One', enterprise_code='EAL-F/FO-MB/2201-01',
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
        inventory_item = baker.make(InventoryItem, item=item, enterprise=enterprise_code)
        baker.make(
            InventoryInventoryItem, inventory=master_inventory, inventory_item=inventory_item)
        baker.make(
            InventoryInventoryItem, inventory=available_inventory, inventory_item=inventory_item)
        section = baker.make(
            Section, section_name='Section A', enterprise=enterprise_code)
        catalog = baker.make(
            Catalog, catalog_name='Elites Age Supermarket Standard Catalog',
            description='Standard Catalog', is_standard=True, enterprise=enterprise_code)
        catalog_item = baker.make(
            CatalogItem, inventory_item=inventory_item, section=section, enterprise=enterprise_code)
        self.recipe = Recipe(
            CatalogCatalogItem, catalog_item=catalog_item, catalog=catalog, enterprise=enterprise_code)

    url = 'v1:catalog:catalogcatalogitem'

    def test_put(self, status_code=200):
        pass

    def test_post(self, status_code=201):
        pass

    def test_patch(self, status_code=200):
        pass
