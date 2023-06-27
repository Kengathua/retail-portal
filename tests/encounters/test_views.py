"""Encounters models test file."""
import json
from django.urls import reverse
from rest_framework.test import APITestCase

from elites_retail_portal.debit.models import (
    Inventory, InventoryItem, InventoryInventoryItem,
    InventoryRecord)
from elites_retail_portal.items.models import (
    Brand, BrandItemType, Category, Item, ItemModel, ItemType,
    ItemUnits, UnitsItemType, Units)
from elites_retail_portal.warehouses.models import (
    Warehouse)
from elites_retail_portal.enterprises.models import Enterprise
from elites_retail_portal.customers.models import Customer
from elites_retail_portal.catalog.models import (
    Catalog, CatalogCatalogItem, CatalogItem)
from elites_retail_portal.encounters.models import Encounter
from elites_retail_portal.enterprise_mgt.models import (
    EnterpriseSetupRule, EnterpriseSetupRuleCatalog,
    EnterpriseSetupRuleInventory, EnterpriseSetupRuleWarehouse)

from tests.utils.login_mixins import authenticate_test_user
from tests.utils.api import APITests

from model_bakery import baker
from model_bakery.recipe import Recipe


class TestEncounterView(APITests, APITestCase):
    """."""

    def setUp(self):
        """."""
        enterprise = baker.make(
            Enterprise, name='Enterprise One', enterprise_code='EAL-E/EO-MB/2301-01',
            business_type='SHOP')
        enterprise_code = enterprise.enterprise_code
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
            ItemModel, brand=brand, item_type=item_type, model_name='GE731K-B SUT',
            enterprise=enterprise_code)
        item_model2 = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='WRTHY46-G DAT',
            enterprise=enterprise_code)
        baker.make(
            Catalog, catalog_name='Elites Age Supermarket Standard Catalog',
            description='Standard Catalog', is_standard=True,
            enterprise=enterprise_code)
        item1 = baker.make(
            Item, item_model=item_model1, barcode='83838388383', make_year=2020,
            enterprise=enterprise_code)
        item2 = baker.make(
            Item, item_model=item_model2, barcode='83838388383', make_year=2020,
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
        inventory = baker.make(
            Inventory, inventory_name='Elites Age Supermarket Available Inventory',
            is_default=True, is_master=True,
            is_active=True, inventory_type='AVAILABLE', enterprise=enterprise_code)
        allocated_inventory = baker.make(
            Inventory, inventory_name='Elites Age Supermarket Allocated Inventory',
            is_active=True, inventory_type='ALLOCATED', enterprise=enterprise_code)
        catalog = baker.make(
            Catalog, catalog_name='Elites Age Supermarket Standard Catalog',
            is_default=True, description='Standard Catalog', is_standard=True,
            enterprise=enterprise_code)
        warehouse = baker.make(
            Warehouse, warehouse_name='Elites Private Warehouse', is_default=True,
            is_receiving=True, enterprise=enterprise_code)
        rule = baker.make(
            EnterpriseSetupRule, name='Elites Age', is_active=True, enterprise=enterprise_code)
        baker.make(
            EnterpriseSetupRuleInventory, rule=rule, inventory=inventory,
            enterprise=enterprise_code)
        baker.make(
            EnterpriseSetupRuleInventory, rule=rule, inventory=allocated_inventory,
            enterprise=enterprise_code)
        baker.make(
            EnterpriseSetupRuleWarehouse, rule=rule, warehouse=warehouse,
            enterprise=enterprise_code)
        baker.make(
            EnterpriseSetupRuleCatalog, rule=rule, catalog=catalog,
            enterprise=enterprise_code)
        inventory_item1 = baker.make(InventoryItem, item=item1, enterprise=enterprise_code)
        inventory_item2 = baker.make(InventoryItem, item=item2, enterprise=enterprise_code)
        baker.make(
            InventoryInventoryItem, inventory=inventory, inventory_item=inventory_item1)
        baker.make(
            InventoryInventoryItem, inventory=inventory, inventory_item=inventory_item2)
        baker.make(
            InventoryInventoryItem, inventory=inventory, inventory_item=inventory_item1)
        baker.make(
            InventoryInventoryItem, inventory=inventory, inventory_item=inventory_item2)
        baker.make(
            InventoryInventoryItem, inventory=allocated_inventory, inventory_item=inventory_item1)
        baker.make(
            InventoryInventoryItem, inventory=allocated_inventory, inventory_item=inventory_item2)
        baker.make(
            InventoryRecord, inventory=inventory, inventory_item=inventory_item1,
            record_type='ADD', quantity_recorded=2, unit_price=1500, enterprise=enterprise_code)
        baker.make(
            InventoryRecord, inventory=inventory, inventory_item=inventory_item2,
            record_type='ADD', quantity_recorded=2, unit_price=2000, enterprise=enterprise_code)
        catalog_item1 = baker.make(
            CatalogItem, inventory_item=inventory_item1, quantity=5, enterprise=enterprise_code)
        catalog_item2 = baker.make(
            CatalogItem, inventory_item=inventory_item2, quantity=6, enterprise=enterprise_code)
        baker.make(CatalogCatalogItem, catalog=catalog, catalog_item=catalog_item1)
        baker.make(CatalogCatalogItem, catalog=catalog, catalog_item=catalog_item2)
        self.customer = baker.make(
            Customer, customer_number=9876, first_name='John',
            last_name='Wick', other_names='Baba Yaga', enterprise=enterprise_code,
            phone_no='+254712345678', email='johnwick@parabellum.com')
        billing = [
            {
                'product': "",
                'serial_number': "",
                'catalog_item': str(catalog_item1.id),
                'item_name': catalog_item1.inventory_item.item.item_name,
                'quantity': 2,
                'unit_price': 1600,
                'total': 3200,
                'deposit': None,
                'sale_type': 'INSTANT'
            },
            {
                'product': "",
                'serial_number': "",
                'catalog_item': str(catalog_item2.id),
                'item_name': catalog_item2.inventory_item.item.item_name,
                'quantity': 3,
                'unit_price': 2300,
                'deposit': 3000,
                'total': 6600,
                'sale_type': 'INSTALLMENT'
            },
        ]
        payments = [
            {
                'means': 'CASH',
                'amount': 5000
            },
            {
                'means': 'MPESA TILL',
                'amount': 2000
            }
        ]

        self.recipe = Recipe(
            Encounter, customer=self.customer, billing=billing,
            payments=payments, submitted_amount=7000, enterprise=enterprise_code)

    url = 'v1:encounters:encounter'

    def test_list(self, status_code=200):
        """."""
        self.client = authenticate_test_user()
        for model in self.get_model()._meta.related_objects:
            model.related_model.objects.all().delete()
        self.get_model().objects.all().delete()
        instance = self.make()
        url = reverse(self.url + '-list')
        resp = self.client.get(url)

        assert resp.status_code == status_code, '{}, {}'.format(resp.content, url)
        if resp.status_code != 200:
            return resp

        assert resp.data['count'] == 1
        assert len(resp.data['results']) == 1
        return instance, resp

    def test_post(self, status_code=201):
        """."""
        self.client = authenticate_test_user()

        test_post_data = self.post_data()
        test_post_data['billing'] = json.dumps(test_post_data['billing'])
        test_post_data['payments'] = json.dumps(test_post_data['payments'])
        test_post_data['customer'] = self.customer.id
        url = reverse(self.url + '-list')
        resp = self.client.post(url, test_post_data)

        assert resp.status_code == status_code, '{}, {}, {}'.format(resp.content, url, test_post_data)  # noqa
        if resp.status_code != 201:
            return resp

        return test_post_data, resp

    def test_put(self, status_code=200):
        """."""
        pass

    def test_get(self, status_code=200):
        """."""
        pass

    def test_delete(self, status_code=204):
        """."""
        pass

    def test_patch(self, status_code=200):
        """."""
        pass

    def test_cancel_receipt(self, status_code=200):
        """."""
        self.client = authenticate_test_user()
        for model in self.get_model()._meta.related_objects:
            model.related_model.objects.all().delete()
        self.get_model().objects.all().delete()
        instance = self.make()
        data = {'note': "Erroneous Payments"}
        url = reverse(
            self.url + '-list') + str(instance.id) + '/cancel_receipt/'
        resp = self.client.post(url, data)
        assert resp.status_code == status_code == 200

        return instance, resp
