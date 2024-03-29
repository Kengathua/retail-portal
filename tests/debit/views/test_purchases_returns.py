"""."""

from tests.utils.api import APITests

from rest_framework.test import APITestCase

from elites_retail_portal.catalog.models import Catalog
from elites_retail_portal.credit.models import PurchaseItem, Purchase
from elites_retail_portal.enterprises.models import Enterprise
from elites_retail_portal.items.models import (
    Brand, BrandItemType, Category, Item, ItemModel, ItemType,
    ItemUnits, UnitsItemType, Units)
from elites_retail_portal.debit.models import (
    Inventory, InventoryInventoryItem, InventoryItem,
    InventoryRecord, PurchasesReturn)
from elites_retail_portal.warehouses.models import Warehouse
from elites_retail_portal.enterprise_mgt.models import (
    EnterpriseSetupRule, EnterpriseSetupRuleInventory,
    EnterpriseSetupRuleCatalog, EnterpriseSetupRuleWarehouse)

from model_bakery import baker
from model_bakery.recipe import Recipe

class TestInventoryView(APITests, APITestCase):
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
            is_receiving=True, enterprise=enterprise_code)
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
        supplier = baker.make(Enterprise, name='LG Supplier')
        purchase = baker.make(
            Purchase, invoice_number='INV-001', supplier=supplier, enterprise=enterprise_code)
        item.activate()
        purchase_item = baker.make(
            PurchaseItem, purchase=purchase, item=item, quantity_purchased=10,
            total_cost=10000, recommended_retail_price=100, quantity_to_inventory=5,
            quantity_to_inventory_on_display=4, enterprise=enterprise_code)
        assert InventoryRecord.objects.count() == 1
        self.recipe = Recipe(
            PurchasesReturn, quantity_returned=5, purchase_item=purchase_item,
            enterprise=enterprise_code)

    url = 'v1:debit:purchasesreturn'

    def test_post(self, status_code=201):
        """."""
        pass

    def test_put(self, status_code=200):
        """."""
        pass

    def test_patch(self, status_code=200):
        """."""
        pass
