"""Enterprise Restrictions Management models file."""

from django.db import models
from django.core.exceptions import ValidationError

from elites_franchise_portal.catalog.models import Catalog
from elites_franchise_portal.common.models import AbstractBase
from elites_franchise_portal.debit.models import Inventory
from elites_franchise_portal.enterprises.models import Enterprise
from elites_franchise_portal.warehouses.models import Warehouse


class EnterpriseSetupRule(AbstractBase):
    """Enterprise Setup Rules model."""
    name = models.CharField(max_length=300)
    inventories = models.ManyToManyField(
        Inventory, through='EnterpriseSetupRuleInventory', related_name='ruleinventory')
    warehouses = models.ManyToManyField(
        Warehouse, through='EnterpriseSetupRuleWarehouse', related_name='rulewarehouse')
    catalogs = models.ManyToManyField(
        Catalog, through='EnterpriseSetupRuleCatalog', related_name='rulecatalog')
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=True)
    supports_installment_sales = models.BooleanField(default=False)

    @property
    def master_inventory(self):
        inventory = self.inventories.filter(enterprise=self.enterprise, is_master=True, is_active=True)
        if not inventory.exists():
            msg = 'You do not have an active master inventory hooked up to the enterprise. Kindly set that up first'
            raise ValidationError(
                {'master_inventory':msg})

        if not inventory.count() == 1:
            msg = 'You can only have one active master inventory hooked up to the enterprise.'
            raise ValidationError(
                {'master_inventory':msg})

        return inventory.first()

    @property
    def allocated_inventory(self):
        inventory = self.inventories.filter(enterprise=self.enterprise,
            inventory_type='ALLOCATED', is_active=True)
        if not inventory.exists():
            msg = 'You do not have an active allocated inventory hooked up to the enterprise. Kindly set that up first'
            raise ValidationError(
                {'allocated_inventory':msg})

        if not inventory.count() == 1:
            msg = 'You can only have one active allocated inventory hooked up to the enterprise.'
            raise ValidationError(
                {'allocated_inventory':msg})

        return inventory.first()

    @property
    def available_inventory(self):
        inventory = self.inventories.filter(enterprise=self.enterprise,
            inventory_type='AVAILABLE', is_active=True)
        if not inventory.exists():
            msg = 'You do not have an active available inventory hooked up to the enterprise. Kindly set that up first'
            raise ValidationError(
                {'available_inventory':msg})

        if not inventory.count() == 1:
            msg = 'You can only have one active available inventory hooked up to the enterprise.'
            raise ValidationError(
                {'available_inventory':msg})

        return inventory.first()

    @property
    def default_inventory(self):
        inventory = self.inventories.filter(enterprise=self.enterprise,
            is_default=True, is_active=True)
        if not inventory.exists():
            msg = 'You do not have an active available inventory hooked up to the enterprise. Kindly set that up first'
            raise ValidationError(
                {'default_inventory':msg})

        if not inventory.count() == 1:
            msg = 'You can only have one active available inventory hooked up to the enterprise.'
            raise ValidationError(
                {'default_inventory':msg})

        return inventory.first()

    @property
    def standard_catalog(self):
        catalog = self.catalogs.filter(
            catalog_type='ON SITE', enterprise=self.enterprise,
            is_standard=True, is_active=True)
        if not catalog.exists():
            msg = 'You do not have an active standard catalog hooked up to the enterprise. Kindly set that up first'
            raise ValidationError(
                {'standard_catalog':msg})

        if not catalog.count() == 1:
            msg = 'You can only have one active available catalog hooked up to the enterprise.'
            raise ValidationError(
                {'standard_catalog':msg})

        return catalog.first()

    @property
    def default_catalog(self):
        catalog = self.catalogs.filter(
            catalog_type='ON SITE', enterprise=self.enterprise,
            is_default=True, is_active=True)
        if not catalog.exists():
            msg = 'You do not have an active standard catalog hooked up to the enterprise. Kindly set that up first'
            raise ValidationError(
                {'standard_catalog':msg})

        if not catalog.count() == 1:
            msg = 'You can only have one active available catalog hooked up to the enterprise.'
            raise ValidationError(
                {'standard_catalog':msg})

        return catalog.first()

    @property
    def default_warehouse(self):
        warehouse = self.warehouses.filter(
            warehouse_type='PRIVATE', enterprise=self.enterprise,
            is_default=True, is_active=True)
        if not warehouse.exists():
            msg = 'You do not have an active default private warehouse hooked up to the enterprise. Kindly set that up first'
            raise ValidationError(
                {'default_warehouse':msg})

        if not warehouse.count() == 1:
            msg = 'You can only have one active default private warehouse hooked up to the enterprise.'
            raise ValidationError(
                {'default_warehouse':msg})

        return warehouse.first()

    @property
    def receiving_warehouse(self):
        warehouse = self.warehouses.filter(
            warehouse_type='PRIVATE', enterprise=self.enterprise,
            is_receiving=True, is_active=True)
        if not warehouse.exists():
            msg = 'You do not have an active receiving private warehouse hooked up to the enterprise. Kindly set that up first'
            raise ValidationError(
                {'receiving_warehouse':msg})

        if not warehouse.count() == 1:
            msg = 'You can only have one active available warehouse hooked up to the enterprise.'
            raise ValidationError(
                {'receiving_warehouse':msg})

        return warehouse.first()

class EnterpriseSetupRuleInventory(AbstractBase):
    rule = models.ForeignKey(EnterpriseSetupRule, on_delete=models.CASCADE)
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def validate_unique_inventory_for_rule(self):
        """Validate an inventory is unique for the given rule."""
        if self.__class__.objects.filter(rule=self.rule, inventory=self.inventory).exclude(id=self.id).exists():
            msg = 'A rule with the inventory {} already exists'.format(self.inventory.inventory_name)
            raise ValidationError(
                {'inventory': msg})

    def clean(self) -> None:
        self.validate_unique_inventory_for_rule()
        return super().clean()


class EnterpriseSetupRuleWarehouse(AbstractBase):
    rule = models.ForeignKey(EnterpriseSetupRule, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def validate_unique_warehouse_for_rule(self):
        """Validate a warehouse is unique for the given rule."""
        if self.__class__.objects.filter(rule=self.rule, warehouse=self.warehouse).exclude(id=self.id).exists():
            msg = 'A rule with the warehouse {} already exists'.format(self.warehouse.warehouse_name)
            raise ValidationError(
                {'warehouse': msg})

    def clean(self) -> None:
        self.validate_unique_warehouse_for_rule()
        return super().clean()


class EnterpriseSetupRuleCatalog(AbstractBase):
    rule = models.ForeignKey(EnterpriseSetupRule, on_delete=models.CASCADE)
    catalog = models.ForeignKey(Catalog, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def validate_unique_catalog_for_rule(self):
        """Validate a catalog is unique for the given rule."""
        if self.__class__.objects.filter(rule=self.rule, catalog=self.catalog).exclude(id=self.id).exists():
            msg = 'A rule with the catalog {} already exists'.format(self.catalog.catalog_name)
            raise ValidationError(
                {'catalog': msg})

    def clean(self) -> None:
        self.validate_unique_catalog_for_rule()
        return super().clean()


class EnterpriseSetup(AbstractBase):
    """Enterprise Setup model."""

    enterprise = models.ForeignKey(
        Enterprise, null=True, blank=True, on_delete=models.CASCADE)
    setup_name = models.CharField(max_length=300)
    is_active = models.BooleanField(default=False)

    @property
    def inventories(self):
        """Get all active inventories for the enterise."""
        active_inventories = Inventory.objects.filter(
            enterprise=self.enterprise, is_active=True)
        active_inventories_names = []
        if active_inventories.exists():
            active_inventories_names = [
                inventory.inventory_name for inventory in active_inventories]
        return active_inventories, active_inventories_names

    @property
    def warehouses(self):
        """Get all warehouses for the enterprise."""
        active_warehouses = Warehouse.objects.filter(
            enterprise=self.enterprise, is_active=True)
        active_warehouses_names = []
        if active_warehouses.exists():
            active_warehouses_names = [
                warehouse.warehouse_name for warehouse in active_warehouses]
        return active_warehouses, active_warehouses_names

    @property
    def catalogs(self):
        """Get all catalogs for the enterprise."""
        active_catalogs = Catalog.objects.filter(enterprise=self.enterprise, is_active=True)
        active_catalogs_names = []
        if active_catalogs.exists():
            active_catalogs_names = [
                catalog.catalog_name for catalog in active_catalogs]
        return active_catalogs, active_catalogs_names
