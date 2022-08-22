"""Inventory views file."""

from elites_franchise_portal.common.views import BaseViewMixin
from elites_franchise_portal.debit.models import (
    Warehouse, WarehouseItem, WarehouseWarehouseItem, WarehouseRecord)
from elites_franchise_portal.debit import serializers
from elites_franchise_portal.debit import filters


class WarehouseViewSet(BaseViewMixin):
    """Warehouse ViewSet class."""

    queryset = Warehouse.objects.all().order_by('warehouse_name')
    serializer_class = serializers.WarehouseSerializer
    filterset_class = filters.WarehouseFilter
    search_fields = ('warehouse_name', 'warehouse_code', 'warehouse_type')


class WarehouseItemViewSet(BaseViewMixin):
    """Warehouse ViewSet class."""

    queryset = WarehouseItem.objects.all().order_by('item__item_name')
    serializer_class = serializers.WarehouseItemSerializer
    filterset_class = filters.WarehouseItemFilter
    search_fields = ('')


class WarehouseWarehouseItemViewSet(BaseViewMixin):
    """Warehouse ViewSet class."""

    queryset = WarehouseWarehouseItem.objects.all().order_by('warehouse__warehouse_name')
    serializer_class = serializers.WarehouseWarehouseItemSerializer
    filterset_class = filters.WarehouseWarehouseItemFilter
    search_fields = ('')


class WarehouseRecordViewSet(BaseViewMixin):
    """Warehouse ViewSet class."""

    queryset = WarehouseRecord.objects.all().order_by('warehouse__warehouse_name', 'warehouse_item__item_name')
    serializer_class = serializers.WarehouseRecordSerializer
    filterset_class = filters.WarehouseRecordFilter
    search_fields = (
        'warehouse__warehouse_name', 'warehouse__warehouse_code',
        'warehouse__warehouse_type')
