"""Debit side serializers."""

from rest_framework.fields import CharField
from rest_framework.fields import SerializerMethodField

from elites_franchise_portal.common.serializers import BaseSerializerMixin
from elites_franchise_portal.debit import models
from elites_franchise_portal.items.models import Item


class InventorySerializer(BaseSerializerMixin):
    """Inventory serializer class."""

    class Meta:
        """Inventory Meta class."""

        model = models.Inventory
        fields = '__all__'


class InventoryItemSerializer(BaseSerializerMixin):
    """Inventory Item serializer class."""

    item_name = CharField(source='item.item_name', read_only=True)

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

    all_data = SerializerMethodField()
    item_name = CharField(source='inventory_item.item.item_name', read_only=True)
    inventory_name = CharField(source='inventory.inventory_name', read_only=True)

    def get_all_data(self, instance):
        """Override all data field to return None.(Optimizing response)."""
        return None

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


class PurchasesReturnSerializer(BaseSerializerMixin):
    """Purchases Return serializer class."""

    class Meta:
        """Purchases Return Meta class."""

        model = models.PurchasesReturn
        fields = '__all__'
