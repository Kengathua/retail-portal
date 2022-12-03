"""Debit side serializers."""

from rest_framework.fields import CharField, SerializerMethodField


from elites_retail_portal.common.serializers import BaseSerializerMixin
from elites_retail_portal.warehouses import models


class WarehouseSerializer(BaseSerializerMixin):
    """Warehouse serializer class."""

    class Meta:
        """Warehouse Meta class."""

        model = models.Warehouse
        fields = '__all__'


class WarehouseItemSerializer(BaseSerializerMixin):
    """Warehouse Item serializer class."""

    item_name = CharField(source='item.item_name', read_only=True)
    barcode = CharField(source='item.barcode', read_only=True)

    class Meta:
        """Warehouse Item Meta class."""

        model = models.WarehouseItem
        fields = '__all__'


class WarehouseWarehouseItemSerializer(BaseSerializerMixin):
    """Warehouse Warehouse Item serializer class."""

    warehouse_name = CharField(source='warehouse.warehouse_name', read_only=True)
    item_name = CharField(source='warehouse_item.item.item_name', read_only=True)
    barcode = CharField(source='warehouse_item.item.barcode', read_only=True)

    class Meta:
        """Meta class."""

        model = models.WarehouseWarehouseItem
        fields = '__all__'


class WarehouseRecordSerializer(BaseSerializerMixin):
    """Store record serializer class."""

    all_data = SerializerMethodField()
    warehouse_name = CharField(source='warehouse.warehouse_name', read_only=True)
    item_name = CharField(source='warehouse_item.item.item_name', read_only=True)
    barcode = CharField(source='warehouse_item.item.barcode', read_only=True)

    def get_all_data(self, instance):
        """Override all data field to return None.(Optimizing response)."""
        return None

    class Meta:
        """Store record Meta class."""

        model = models.WarehouseRecord
        fields = '__all__'
