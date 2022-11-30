"""Inventory views file."""

from elites_retail_portal.common.views import BaseViewMixin
from elites_retail_portal.debit.models import (
    Inventory, InventoryItem, InventoryRecord)
from elites_retail_portal.debit import serializers
from elites_retail_portal.debit import filters
from elites_retail_portal.debit.models.inventory import InventoryInventoryItem


class InventoryViewSet(BaseViewMixin):
    """Inventory Viewset class."""

    queryset = Inventory.objects.all().order_by('inventory_name')
    serializer_class = serializers.InventorySerializer
    filterset_class = filters.InventoryFilter
    search_fields = (
        'inventory_name', 'inventory_code', 'inventory_type')


class InventoryItemViewSet(BaseViewMixin):
    """Inventory Item Viewset class."""

    queryset = InventoryItem.objects.all().order_by('item__item_name')
    serializer_class = serializers.InventoryItemSerializer
    filterset_class = filters.InventoryItemFilter
    search_fields = (
        'item__item_name', 'item__item_model__model_name',
        'item__item_model__model_code', 'item__barcode',
        'item__item_code', 'item__make_year',
    )


class InventoryInventoryItemViewSet(BaseViewMixin):
    """Inventory Inventory Item Viewset class."""

    queryset = InventoryInventoryItem.objects.all().order_by(
        'inventory__inventory_name', 'inventory_item__item__item_name')
    serializer_class = serializers.InventoryInventoryItemSerializer
    filterset_class = filters.InventoryInventoryItemFilter
    search_fields = (
        'inventory__inventory_name', 'inventory__inventory_code',
        'inventory__inventory_type', 'inventory_item__item__item_name',
        'inventory_item__item__item_model__model_name',
        'inventory_item__item__item_model__model_code',
        'inventory_item__item__barcode', 'inventory_item__item__item_code',
        'inventory_item__item__make_year',
        )


class InventoryRecordViewSet(BaseViewMixin):
    """Inventory Record ViewSet class."""

    queryset = InventoryRecord.objects.all().order_by(
        '-updated_on', 'inventory_item__item__item_name')
    serializer_class = serializers.InventoryRecordSerializer
    filterset_class = filters.InventoryRecordFilter
    search_fields = (
        'inventory__inventory_name', 'inventory__inventory_code',
        'inventory__inventory_type', 'inventory_item__item__item_name',
        'inventory_item__item__item_model__model_name',
        'inventory_item__item__item_model__model_code',
        'inventory_item__item__barcode', 'inventory_item__item__item_code',
        'inventory_item__item__make_year', 'record_code', 'record_type', 'removal_type',
        )
