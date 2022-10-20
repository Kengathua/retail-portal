"""."""

import pytest
from rest_framework.test import APITestCase

from tests.utils.api import APITests
from elites_franchise_portal.enterprises.models import Enterprise
from elites_franchise_portal.items.models import (
    Brand, BrandItemType, Category, Item, ItemModel, ItemType)
from elites_franchise_portal.warehouses.models import (
    Warehouse, WarehouseItem, WarehouseRecord, WarehouseWarehouseItem)

from tests.utils.login_mixins import LoggedInMixin, authenticate_test_user

from model_bakery import baker
from model_bakery.recipe import Recipe, foreign_key

pytestmark = pytest.mark.django_db


class TestWarehouseView(APITests, APITestCase):

    def setUp(self):
        enterprise = baker.make(
            Enterprise, name='Enterprise One', enterprise_type='FRANCHISE', business_type='SHOP')
        enterprise_code = enterprise.enterprise_code
        self.recipe = Recipe(Warehouse, warehouse_name='Elites Private Warehouse', enterprise=enterprise_code)

    url = 'v1:warehouses:warehouse'


class TestWarehouseItemView(APITests, APITestCase):

    def setUp(self):
        enterprise = baker.make(
            Enterprise, name='Enterprise One', enterprise_type='FRANCHISE', business_type='SHOP')
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
        item_model = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731K-B SUT',
            enterprise=enterprise_code)
        item = baker.make(
            Item, item_model=item_model, barcode='83838388383', make_year=2020,
            enterprise=enterprise_code)
        self.recipe = Recipe(WarehouseItem, item=item, enterprise=enterprise_code)

    url = 'v1:warehouses:warehouseitem'


class TestWarehouseWarehouseItemView(APITests, APITestCase):

    def setUp(self):
        enterprise = baker.make(
            Enterprise, name='Enterprise One', enterprise_type='FRANCHISE', business_type='SHOP')
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
        item_model = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731K-B SUT',
            enterprise=enterprise_code)
        item = baker.make(
            Item, item_model=item_model, barcode='83838388383', make_year=2020,
            enterprise=enterprise_code)
        warehouse = baker.make(
            Warehouse, warehouse_name='Elites Private Warehouse', enterprise=enterprise_code)
        warehouse_item = baker.make(WarehouseItem, item=item, enterprise=enterprise_code)

        self.recipe = Recipe(
            WarehouseWarehouseItem, warehouse=warehouse, warehouse_item=warehouse_item,
            enterprise=enterprise_code)

    url = 'v1:warehouses:warehousewarehouseitem'


class TestWarehouseRecordView(APITests, APITestCase):
    """TestWarehouseRecordView."""

    def setUp(self):
        """."""
        enterprise = baker.make(
            Enterprise, name='Enterprise One', enterprise_type='FRANCHISE', business_type='SHOP')
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
        item_model = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731K-B SUT',
            enterprise=enterprise_code)
        item = baker.make(
            Item, item_model=item_model, barcode='83838388383', make_year=2020,
            enterprise=enterprise_code)
        warehouse = baker.make(
            Warehouse, warehouse_name='Elites Private Warehouse', enterprise=enterprise_code)
        warehouse_item = baker.make(WarehouseItem, item=item, enterprise=enterprise_code)
        self.recipe = Recipe(
            WarehouseRecord, warehouse_item=warehouse_item, warehouse=warehouse, record_type='ADD',
            quantity_recorded=15, unit_price=300, enterprise=enterprise_code)

    url = 'v1:warehouses:warehouserecord'
