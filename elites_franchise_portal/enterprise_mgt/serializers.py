"""Restriction Rules serializers file."""

from rest_framework.fields import SerializerMethodField, ReadOnlyField

from elites_franchise_portal.common.serializers import BaseSerializerMixin
from elites_franchise_portal.enterprise_mgt import models


class EnterpriseSetupSerializer(BaseSerializerMixin):
    """EnterpriseSetup Serializer class."""

    inventories = SerializerMethodField()
    warehouses = SerializerMethodField()
    catalogs = SerializerMethodField()

    def get_inventories(self, instance):
        """Get inventories."""
        inventories, inventories_names = instance.inventories
        all_inventories = []
        for inventory in inventories:
            inventory_data = {
                'id': inventory.id,
                'inventory_name': inventory.inventory_name,
                'inventory_code': inventory.inventory_code
            }
            all_inventories.append(inventory_data)
        return all_inventories

    def get_warehouses(self, instance):
        """Get warehouses."""
        warehouses, warehouses_names = instance.warehouses
        all_warehouses = []
        for warehouse in warehouses:
            warehouse_data = {
                'id': warehouse.id,
                'warehouse_name': warehouse.warehouse_name,
                'warehouse_code': warehouse.warehouse_code
            }
            all_warehouses.append(warehouse_data)
        return all_warehouses

    def get_catalogs(self, instance):
        """Get catalogs."""
        catalogs, catalogs_names = instance.catalogs
        all_catalogs = []
        for catalog in catalogs:
            catalog_data = {
                'id': catalog.id,
                'catalog_name': catalog.catalog_name,
                'catalog_code': catalog.catalog_code
            }
            all_catalogs.append(catalog_data)
        return all_catalogs

    class Meta:
        """EnterpriseSetup serializer Meta class."""

        model = models.EnterpriseSetup
        fields = '__all__'


class EnterpriseSetupRuleSerializer(BaseSerializerMixin):
    """EnterpriseSetupRule Serializer class."""

    class Meta:
        """EnterpriseSetupRule serializer Meta class."""

        model = models.EnterpriseSetupRule
        fields = '__all__'


class EnterpriseSetupRuleInventorySerializer(BaseSerializerMixin):
    """EnterpriseSetupRule Inventory Serializer"""

    inventory_name = ReadOnlyField(source='inventory.inventory_name')
    is_master_inventory = ReadOnlyField(source='inventory.is_master')
    inventory_type = ReadOnlyField(source='inventory.inventory_type')

    class Meta:
        """EnterpriseSetupRuleInventory serializer Meta class."""

        model = models.EnterpriseSetupRuleInventory
        fields = '__all__'


class EnterpriseSetupRuleWarehouseSerializer(BaseSerializerMixin):
    """EnterpriseSetupRule Warehouse Serializer"""

    warehouse_name = ReadOnlyField(source='warehouse.warehouse_name')
    is_default_warehouse = ReadOnlyField(source='warehouse.is_default')
    warehouse_type = ReadOnlyField(source='warehouse.warehouse_type')
    is_receiving_warehouse = ReadOnlyField(source='warehouse.is_receiving')

    class Meta:
        """EnterpriseSetupRuleWarehouse serializer Meta class."""

        model = models.EnterpriseSetupRuleWarehouse
        fields = '__all__'


class EnterpriseSetupRuleCatalogSerializer(BaseSerializerMixin):
    """EnterpriseSetupRule Catalog Serializer"""

    catalog_name = ReadOnlyField(source='catalog.catalog_name')
    catalog_type = ReadOnlyField(source='catalog.catalog_type')
    is_standard_catalog = ReadOnlyField(source='catalog.is_standard')

    class Meta:
        """EnterpriseSetupRuleCatalog serializer Meta class."""

        model = models.EnterpriseSetupRuleCatalog
        fields = '__all__'
