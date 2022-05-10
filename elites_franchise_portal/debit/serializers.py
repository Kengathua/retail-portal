"""Debit side serializers."""

from rest_framework.fields import SerializerMethodField

from elites_franchise_portal.common.serializers import BaseSerializerMixin
from elites_franchise_portal.debit import models
from elites_franchise_portal.items.models import Item


class StoreSerializer(BaseSerializerMixin):
    """Store serializer class."""

    class Meta:
        """Store Meta class."""

        model = models.Store
        fields = '__all__'


class StoreRecordSerializer(BaseSerializerMixin):
    """Store record serializer class."""

    store_item = SerializerMethodField()

    def get_store_item(self, record):
        """Serialize details of the business partner that a user is linked to."""
        store = models.Store.objects.get(id=record.store.id)
        return {
            'id': store.id,
            'item_name': store.item.item_name,
            'store_code': store.store_code
        }

    class Meta:
        """Store record Meta class."""

        model = models.StoreRecord
        fields = '__all__'


class InventoryItemSerializer(BaseSerializerMixin):
    """Inventory Item serializer class."""

    class Meta:
        """Inventory item Meta class."""

        model = models.InventoryItem
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
