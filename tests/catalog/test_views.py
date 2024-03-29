"""Catalog views file."""

import json

from tests.utils.api import APITests
from rest_framework.test import APITestCase
from django.urls import reverse

from elites_retail_portal.items.models import (
    Brand, BrandItemType, Category, Item, ItemModel, ItemType,
    ItemUnits, UnitsItemType, Units, Product)
from elites_retail_portal.catalog.models import (
    Section, Catalog, CatalogItem, CatalogCatalogItem, CatalogItemAuditLog)
from elites_retail_portal.debit.models import (
    Inventory, InventoryItem, InventoryRecord, InventoryInventoryItem)
from elites_retail_portal.enterprises.models import Enterprise
from tests.utils.login_mixins import authenticate_test_user
from elites_retail_portal.enterprise_mgt.models import (
    EnterpriseSetupRule, EnterpriseSetupRuleCatalog,
    EnterpriseSetupRuleInventory, EnterpriseSetupRuleWarehouse)
from elites_retail_portal.warehouses.models import Warehouse

from model_bakery import baker
from model_bakery.recipe import Recipe


class TestSectionView(APITests, APITestCase):
    """."""

    def setUp(self):
        """."""
        # using the Setup function helps avoid using recipes for foregn keys
        # or the django db mark error
        enterprise = baker.make(
            Enterprise, name='Enterprise One', enterprise_type='FRANCHISE')
        enterprise_code = enterprise.enterprise_code
        self.recipe = Recipe(
            Section, section_name='Section A', enterprise=enterprise_code)

    url = 'v1:catalog:section'


class TestCatalogView(APITests, APITestCase):
    def setUp(self):
        franchise = baker.make(
            Enterprise, name='Enterprise One', enterprise_code='EAL-E/EO-MB/2301-01',
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
            Enterprise, name='Enterprise One', enterprise_code='EAL-E/EO-MB/2301-01',
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
        inventory = baker.make(
            Inventory, inventory_name='Elites Age Supermarket Available Inventory',
            is_default=True, is_master=True,
            is_active=True, inventory_type='AVAILABLE', enterprise=enterprise_code)
        self.catalog = baker.make(
            Catalog, catalog_name='Elites Age Supermarket Standard Catalog',
            is_default=True,
            description='Standard Catalog', is_standard=True, enterprise=enterprise_code)
        warehouse = baker.make(
            Warehouse, warehouse_name='Elites Private Warehouse', is_default=True,
            is_receiving=True,
            enterprise=enterprise_code)
        rule = baker.make(
            EnterpriseSetupRule, name='Elites Age', is_active=True, enterprise=enterprise_code)
        baker.make(
            EnterpriseSetupRuleInventory, rule=rule, inventory=inventory,
            enterprise=enterprise_code)
        baker.make(
            EnterpriseSetupRuleWarehouse, rule=rule, warehouse=warehouse,
            enterprise=enterprise_code)
        baker.make(
            EnterpriseSetupRuleCatalog, rule=rule, catalog=self.catalog,
            enterprise=enterprise_code)
        inventory_item = baker.make(InventoryItem, item=item, enterprise=enterprise_code)
        baker.make(
            InventoryInventoryItem, inventory=inventory, inventory_item=inventory_item)
        baker.make(
            InventoryRecord, inventory=inventory, inventory_item=inventory_item,
            record_type='ADD', quantity_recorded=15, unit_price=300, enterprise=enterprise_code)
        section = baker.make(
            Section, section_name='Section A', enterprise=enterprise_code)
        self.recipe = Recipe(
            CatalogItem, inventory_item=inventory_item, section=section, enterprise=enterprise_code)

    url = 'v1:catalog:catalogitem'

    def test_post(self, status_code=201):
        """."""
        self.client = authenticate_test_user()
        catalog_item = self.make()
        CatalogItemAuditLog.objects.all().delete()
        CatalogItem.objects.all().delete()
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

    def test_delete(self, status_code=204):
        pass

    def test_add_to_catalogs(self, status_code=200):
        self.client = authenticate_test_user()
        catalog_item = self.recipe.make()
        url = reverse(self.url + '-detail', kwargs={self.id_field: catalog_item.id})
        url = url + 'add_to_catalogs/'
        payload = {'catalogs': [str(self.catalog.id)]}
        resp = self.client.post(url, payload)

        assert resp.status_code == status_code


class TestCatalogCatalogItemView(APITests, APITestCase):
    """."""

    def setUp(self):
        """."""
        franchise = baker.make(
            Enterprise, name='Enterprise One', enterprise_code='EAL-E/EO-MB/2301-01',
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
            is_receiving=True,
            enterprise=enterprise_code)
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
        baker.make(
            InventoryInventoryItem, inventory=inventory, inventory_item=inventory_item)
        section = baker.make(
            Section, section_name='Section A', enterprise=enterprise_code)
        self.catalog = baker.make(
            Catalog, catalog_name='Elites Age Supermarket Standard Catalog',
            description='Standard Catalog', is_standard=True, enterprise=enterprise_code)
        catalog_item = baker.make(
            CatalogItem, inventory_item=inventory_item, section=section, enterprise=enterprise_code)
        self.recipe = Recipe(
            CatalogCatalogItem, catalog_item=catalog_item, catalog=self.catalog, enterprise=enterprise_code)

    url = 'v1:catalog:catalogcatalogitem'

    def test_put(self, status_code=200):
        pass

    def test_post(self, status_code=201):
        pass

    def test_patch(self, status_code=200):
        pass
