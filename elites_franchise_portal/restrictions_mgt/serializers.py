"""Restriction Rules serializers file."""

from django.core.serializers import serialize
from rest_framework.fields import CharField, SerializerMethodField

from elites_franchise_portal.common.serializers import BaseSerializerMixin
from elites_franchise_portal.restrictions_mgt import models
from elites_franchise_portal.debit.serializers import InventoryItemSerializer


from django.core.serializers.json import DjangoJSONEncoder

class LazyEncoder(DjangoJSONEncoder):
    def default(self, obj):
        # if isinstance(obj, YourCustomType):
        #     return str(obj)
        return super().default(obj)

class EnterpriseSetupSerializer(BaseSerializerMixin):
    """EnterpriseSetup Serializer class."""

    inventories = SerializerMethodField()
    warehouses = SerializerMethodField()
    catalogs = SerializerMethodField()

    def get_inventories(self, instance):
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


class EnterpriseSetupRulesSerializer(BaseSerializerMixin):
    """EnterpriseSetupRules Serializer class."""

    class Meta:
        """EnterpriseSetupRules serializer Meta class."""

        model = models.EnterpriseSetupRules
        fields = '__all__'