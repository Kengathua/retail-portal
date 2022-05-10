"""."""
from rest_framework.test import APITestCase
from tests.utils.api import APITests

from elites_franchise_portal.franchises.models import Franchise
from elites_franchise_portal.items.models import (
    Brand, BrandItemType, Category, Item, ItemModel, ItemType,
    ItemUnits, UnitsItemType, Units)
from elites_franchise_portal.debit.models import (
    InventoryItem, InventoryRecord, Store, StoreRecord,
    Sale, SaleRecord)
from elites_franchise_portal.credit.models import *
from elites_franchise_portal.credit.models import Purchase

from model_bakery import baker
from model_bakery.recipe import Recipe, foreign_key


class TestPurchasesView(APITests, APITestCase):
    """."""

    def setUp(self):
        """."""
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
            franchise=franchise_code)
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
        self.recipe = Recipe(
            Purchase, item=item, quantity_purchased=10, total_price=10000,
            unit_marked_price=100, quantity_to_inventory=40,
            quantity_to_inventory_on_display=10, quantity_to_inventory_in_store=30,
            franchise=franchise_code)

    url = 'v1:credit:purchase'

    def test_post(self, status_code=201):
        """."""
        pass

    def test_patch(self, status_code=200):
        """."""
        pass

    def test_put(self, status_code=200):
        """."""
        pass
