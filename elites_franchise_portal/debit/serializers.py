"""Debit side serializers."""

from rest_framework.fields import SerializerMethodField

from elites_franchise_portal.common.serializers import BaseSerializerMixin
from elites_franchise_portal.debit import models
from elites_franchise_portal.items.models import Item


class WarehouseSerializer(BaseSerializerMixin):
    """Warehouse serializer class."""

    class Meta:
        """Warehouse Meta class."""

        model = models.Warehouse
        fields = '__all__'

class WarehouseItemSerializer(BaseSerializerMixin):
    """Warehouse Item serializer class."""

    class Meta:
        """Warehouse Item Meta class."""
        model = models.WarehouseItem
        fields = '__all__'

class WarehouseWarehouseItemSerializer(BaseSerializerMixin):
    """Warehouse Warehouse Item serializer class."""

    class Meta:
        """Meta class."""
        model = models.WarehouseWarehouseItem
        fields = '__all__'

class WarehouseRecordSerializer(BaseSerializerMixin):
    """Store record serializer class."""

    class Meta:
        """Store record Meta class."""

        model = models.WarehouseRecord
        fields = '__all__'


class InventorySerializer(BaseSerializerMixin):
    """Inventory serializer class."""

    class Meta:
        """Inventory Meta class."""

        model = models.Inventory
        fields = '__all__'


class InventoryItemSerializer(BaseSerializerMixin):
    """Inventory Item serializer class."""

    class Meta:
        """Inventory item Meta class."""

        model = models.InventoryItem
        fields = '__all__'


class InventoryInventoryItemSerializer(BaseSerializerMixin):
    """Inventory Inventory Item serializer class."""

    class Meta:
        """Inventory Inventory Item Meta class."""

        model = models.InventoryInventoryItem
        fields = '__all__'


class InventoryRecordSerializer(BaseSerializerMixin):
    """Inventory record serializer class."""

    item = SerializerMethodField()

    def get_item(self, record):
        """Serialize details of the business partner that a user is linked to."""
        item = Item.objects.get(id=record.inventory_item.item.id)
        return {
            'id': item.id,
            'item_name': item.item_name,
        }

    class Meta:
        """Inventory record Meta class."""

        model = models.InventoryRecord
        fields = '__all__'


class SaleSerializer(BaseSerializerMixin):
    """Sale serializer class."""

    class Meta:
        """Sale Meta class."""

        model = models.Sale
        fields = '__all__'


class SaleRecordSerializer(BaseSerializerMixin):
    """Sale Record serializer class."""

    class Meta:
        """Sale Record Meta class."""

        model = models.SaleRecord
        fields = '__all__'
