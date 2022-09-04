"""Inventory views file."""

from elites_franchise_portal.common.views import BaseViewMixin
from elites_franchise_portal.debit.models import (
    Inventory, InventoryItem, InventoryRecord)
from elites_franchise_portal.debit import serializers
from elites_franchise_portal.debit import filters
from elites_franchise_portal.debit.models.inventory import InventoryInventoryItem


class InventoryViewSet(BaseViewMixin):
    """Inventory Viewset class."""

    queryset = Inventory.objects.all().order_by('inventory_name')
    serializer_class = serializers.InventorySerializer
    filterset_class = filters.InventoryFilter
    search_fields = ('inventory_name')


class InventoryItemViewSet(BaseViewMixin):
    """Inventory Item Viewset class."""

    queryset = InventoryItem.objects.all().order_by('item__item_name')
    serializer_class = serializers.InventoryItemSerializer
    filterset_class = filters.InventoryItemFilter
    search_fields = ('')


class InventoryInventoryItemViewSet(BaseViewMixin):
    """Inventory Inventory Item Viewset class."""

    queryset = InventoryInventoryItem.objects.all().order_by('inventory__inventory_name', 'inventory_item__item__item_name')
    serializer_class = serializers.InventoryInventoryItemSerializer
    filterset_class = filters.InventoryInventoryItemFilter
    search_fields = ('')


class InventoryRecordViewSet(BaseViewMixin):
    """Inventory Record ViewSet class."""

    queryset = InventoryRecord.objects.all().order_by('inventory_item__item__item_name')
    serializer_class = serializers.InventoryRecordSerializer
    filterset_class = filters.InventoryRecordFilter
    search_fields = ('')
