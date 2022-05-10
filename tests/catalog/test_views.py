from socket import CAN_RAW
from tests.utils.api import APITests
from rest_framework.test import APITestCase

from elites_franchise_portal.items.models import (
    Brand, BrandItemType, Category, Item, ItemModel, ItemType,
    ItemUnits, UnitsItemType, Units)
from elites_franchise_portal.debit.models import (
    InventoryItem, InventoryRecord, Sale, SaleRecord)
from elites_franchise_portal.catalog.models import (
    Section, Catalog, CatalogItem, CatalogCatalogItem)
from elites_franchise_portal.franchises.models import Franchise

from model_bakery import baker
from model_bakery.recipe import Recipe, foreign_key

class TestSectionView(APITests, APITestCase):
    def setUp(self):
        # using the Setup function helps avoid using recipes for foregn keys
        # or the django db mark error
        franchise = baker.make(
            Franchise, name='Franchise One', elites_code='EAL-F/FO-MB/2201-01',
            partnership_type='SHOP')
        franchise_code = franchise.elites_code
        self.recipe = Recipe(
            Section, section_name='Section A', franchise=franchise_code)

    url = 'v1:catalog:section'


class TestCatalogView(APITests, APITestCase):
    def setUp(self):
        franchise = baker.make(
            Franchise, name='Franchise One', elites_code='EAL-F/FO-MB/2201-01',
            partnership_type='SHOP')
        franchise_code = franchise.elites_code
        self.recipe = Recipe(
            Catalog, name='Elites Age Supermarket Standard Catalog',
            description='Standard Catalog', is_standard_catalog=True, franchise=franchise_code)

    url = 'v1:catalog:catalog'


class TestCatalogItemView(APITests, APITestCase):
    def setUp(self):
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
            quantity_recorded=15, unit_price=300, franchise=franchise_code)
        section = baker.make(
            Section, section_name='Section A', franchise=franchise_code)
        self.recipe = Recipe(
            CatalogItem, inventory_item=inventory_item, section=section, franchise=franchise_code)

    url = 'v1:catalog:catalogitem'


class TestCatalogCatalogItemView(APITests, APITestCase):
    def setUp(self):
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
        section = baker.make(
            Section, section_name='Section A', franchise=franchise_code)
        catalog = baker.make(
            Catalog, name='Elites Age Supermarket Standard Catalog',
            description='Standard Catalog', is_standard_catalog=True, franchise=franchise_code)
        catalog_item = baker.make(
            CatalogItem, inventory_item=inventory_item, section=section, franchise=franchise_code)
        self.recipe = Recipe(
            CatalogCatalogItem, catalog_item=catalog_item, catalog=catalog, franchise=franchise_code)

    url = 'v1:catalog:catalogcatalogitem'
