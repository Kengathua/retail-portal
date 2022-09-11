from elites_franchise_portal.restrictions_mgt.models import EnterpriseSetupRules
import pytest
from django.test import TestCase
from django.core.exceptions import ValidationError

from elites_franchise_portal.enterprises.models import Enterprise
from elites_franchise_portal.items.models import (
    Brand, BrandItemType, Category, Item, ItemModel, ItemType,
    ItemUnits, UnitsItemType, Units)
from elites_franchise_portal.debit.models import (
    InventoryItem, Inventory, InventoryInventoryItem, Sale, SaleRecord)
from elites_franchise_portal.catalog.models import (
    Section, Catalog, CatalogItem, CatalogCatalogItem, ReferenceCatalog)
from elites_franchise_portal.warehouses.models import Warehouse


from model_bakery import baker

class TestEnterPriseSetupRules(TestCase):
    """."""

    def setUp(self) -> None:
        self.enterprise = baker.make(
            Enterprise, name='Enterprise One', enterprise_code='EAL-E/FO-MB/2201-01',
            enterprise_type='FRANCHISE', business_type='SHOP')
        self.enterprise_code = self.enterprise.enterprise_code
        self.master_inventory = baker.make(
            Inventory, inventory_name='Elites Age Supermarket Working Stock Inventory',
            is_master=True, is_active=True, inventory_type='WORKING STOCK',
            enterprise=self.enterprise_code)
        self.default_inventory = baker.make(
            Inventory, inventory_name='Elites Age Supermarket Available Inventory',
            is_active=True, inventory_type='AVAILABLE', enterprise=self.enterprise_code)
        self.standard_catalog = baker.make(
            Catalog, catalog_name='Elites Age Supermarket Standard Catalog',
            description='Standard Catalog', is_standard=True, enterprise=self.enterprise_code)
        self.receiving_warehouse = baker.make(
            Warehouse, warehouse_name='Elites Private Warehouse', enterprise=self.enterprise_code)
        self.enterprise_setup_rules = baker.make(
            EnterpriseSetupRules, master_inventory=self.master_inventory,
            default_inventory=self.default_inventory, receiving_warehouse=self.receiving_warehouse,
            default_warehouse=self.receiving_warehouse, standard_catalog=self.standard_catalog,
            default_catalog=self.standard_catalog, is_active=True, enterprise=self.enterprise_code)

        return super().setUp()

    def test_pass(self):
        pass
