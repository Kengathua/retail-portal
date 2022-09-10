"""Enterprise Restrictions Management models file."""

from django.db import models

from elites_franchise_portal.common.models import AbstractBase
from elites_franchise_portal.debit.models import Inventory
from elites_franchise_portal.warehouses.models import Warehouse
from elites_franchise_portal.catalog.models import Catalog
from elites_franchise_portal.enterprises.models import Enterprise


class EnterpriseSetupRules(AbstractBase):
    """Enterprise Setup Rules model."""

    master_inventory = models.ForeignKey(
        Inventory, related_name='master_inventory', on_delete=models.CASCADE)
    default_inventory = models.ForeignKey(
        Inventory, related_name='default_inventory', on_delete=models.CASCADE)
    receiving_warehouse = models.ForeignKey(
        Warehouse, related_name='receiving_warehouse', on_delete=models.CASCADE)
    default_warehouse = models.ForeignKey(
        Warehouse, related_name='default_warehouse', on_delete=models.CASCADE)
    standard_catalog = models.ForeignKey(
        Catalog, related_name='standard_catalog', on_delete=models.CASCADE)
    default_catalog = models.ForeignKey(
        Catalog, related_name='default_catalog', on_delete=models.CASCADE)


class EnterpriseSetup(AbstractBase):
    """Enterprise Setup model."""

    enterprise = models.ForeignKey(
        Enterprise, null=True, blank=True, on_delete=models.CASCADE)
    setup_name = models.CharField(max_length=300)
    is_active = models.BooleanField(default=False)

    @property
    def inventories(self):
        active_inventories = Inventory.objects.filter(
            enterprise=self.enterprise, is_active=True)
        active_inventories_names = []
        if active_inventories.exists():
            active_inventories_names = [
                inventory.inventory_name for inventory in active_inventories]
        return active_inventories, active_inventories_names

    @property
    def warehouses(self):
        active_warehouses = Warehouse.objects.filter(
            enterprise=self.enterprise, is_active=True)
        active_warehouses_names = []
        if active_warehouses.exists():
            active_warehouses_names = [
                warehouse.warehouse_name for warehouse in active_warehouses]
        return active_warehouses, active_warehouses_names

    @property
    def catalogs(self):
        active_catalogs = Catalog.objects.filter(enterprise=self.enterprise, is_active=True)
        active_catalogs_names = []
        if active_catalogs.exists():
            active_catalogs_names = [
                catalog.catalog_name for catalog in active_catalogs]
        return active_catalogs, active_catalogs_names
