from elites_retail_portal.enterprise_mgt.models import EnterpriseSetupRule
from django.test import TestCase

from elites_retail_portal.enterprises.models import Enterprise
from elites_retail_portal.debit.models import Inventory
from elites_retail_portal.catalog.models import Catalog
from elites_retail_portal.warehouses.models import Warehouse


from model_bakery import baker

class TestEnterpriseSetupRule(TestCase):
    """."""

    def setUp(self) -> None:
        self.enterprise = baker.make(
            Enterprise, name='Enterprise One', enterprise_code='EAL-E/EO-MB/2201-01',
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
        self.default_catalog = self.standard_catalog
        self.receiving_warehouse = baker.make(
            Warehouse, warehouse_name='Elites Private Warehouse', is_default=True,
            enterprise=self.enterprise_code)
        self.enterprise_setup_rules = baker.make(
            EnterpriseSetupRule, master_inventory=self.master_inventory,
            default_inventory=self.default_inventory, receiving_warehouse=self.receiving_warehouse,
            default_warehouse=self.receiving_warehouse, standard_catalog=self.standard_catalog,
            default_catalog=self.standard_catalog, is_active=True, enterprise=self.enterprise_code)

        return super().setUp()

    def test_pass(self):
        pass
