"""Inventory views file."""

from elites_franchise_portal.common.views import BaseViewMixin
from elites_franchise_portal.debit.models import (
    Store, StoreRecord, InventoryItem, InventoryRecord)
from elites_franchise_portal.debit.serializers import (
    StoreSerializer, StoreRecordSerializer, InventoryItemSerializer,
    InventoryRecordSerializer)
from elites_franchise_portal.debit import filters


class StoreViewSet(BaseViewMixin):
    """Store ViewSet class."""

    queryset = Store.objects.all().order_by('item__item_name')
    serializer_class = StoreSerializer
    filterset_class = filters.StoreFilter
    search_fields = ('')


class StoreRecordViewSet(BaseViewMixin):
    """Store Record Viewset class."""

    queryset = StoreRecord.objects.all().order_by('store__item__item_name')
    serializer_class = StoreRecordSerializer
    filterset_class = filters.StoreRecordFilter
    search_fields = ('')


class InventoryItemViewSet(BaseViewMixin):
    """Inventory Item Viewset class."""

    queryset = InventoryItem.objects.all().order_by('item__item_name')
    serializer_class = InventoryItemSerializer
    filterset_class = filters.InventoryItemFilter
    search_fields = ('')


class InventoryRecordViewSet(BaseViewMixin):
    """Inventory Record ViewSet class."""

    queryset = InventoryRecord.objects.all().order_by('inventory_item__item__item_name')
    serializer_class = InventoryRecordSerializer
    filterset_class = filters.InventoryRecordFilter
    search_fields = ('')
