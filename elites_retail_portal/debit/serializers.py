"""Debit side serializers."""

from rest_framework.fields import (
    SerializerMethodField, ReadOnlyField, CharField)

from elites_retail_portal.common.serializers import BaseSerializerMixin
from elites_retail_portal.debit import models


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

    customer_name = ReadOnlyField(source='customer.full_name')
    order_number = CharField(source='order.order_number', read_only=True)

    class Meta:
        """Sale Meta class."""

        model = models.Sale
        fields = '__all__'


class SaleItemSerializer(BaseSerializerMixin):
    """Sale Item serializer class."""

    item_name = CharField(source='catalog_item.inventory_item.item.item_name', read_only=True)

    class Meta:
        """Sale Item Meta class."""

        model = models.SaleItem
        fields = '__all__'


class PurchasesReturnSerializer(BaseSerializerMixin):
    """Purchases Return serializer class."""

    item_name = ReadOnlyField(source='purchase_item.item.item_name')
    purchase = ReadOnlyField(source='purchase.id')

    class Meta:
        """Purchases Return Meta class."""

        model = models.PurchasesReturn
        fields = '__all__'
