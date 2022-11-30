"""Debit side filters file."""

from elites_retail_portal.common.filters import SearchComboboxBaseFilter
from elites_retail_portal.warehouses import models


class WarehouseFilter(SearchComboboxBaseFilter):
    """Filter individual item store."""

    class Meta:
        """Restrict filter fields."""

        model = models.Warehouse
        fields = '__all__'


class WarehouseItemFilter(SearchComboboxBaseFilter):
    """Filter individual item store."""

    class Meta:
        """Restrict filter fields."""

        model = models.WarehouseItem
        fields = '__all__'


class WarehouseWarehouseItemFilter(SearchComboboxBaseFilter):
    """Filter WarehouseWarehouseItem."""

    class Meta:
        """."""

        model = models.WarehouseWarehouseItem
        fields = '__all__'


class WarehouseRecordFilter(SearchComboboxBaseFilter):
    """Filter individual item store record."""

    class Meta:
        """Restrict filter fields."""

        model = models.WarehouseRecord
        fields = '__all__'
