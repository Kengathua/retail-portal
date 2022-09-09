"""Debit side filters file."""
from elites_franchise_portal.common.filters import SearchComboboxBaseFilter
from elites_franchise_portal.debit import models


class InventoryFilter(SearchComboboxBaseFilter):
    """Filter inventory."""

    class Meta:
        """Restrict filter fields."""

        model = models.Inventory
        fields = '__all__'


class InventoryItemFilter(SearchComboboxBaseFilter):
    """Filter individual item inventory item."""

    class Meta:
        """Restrict filter fields."""

        model = models.InventoryItem
        fields = '__all__'


class InventoryInventoryItemFilter(SearchComboboxBaseFilter):
    """Filter Inventory Inventory Item."""

    class Meta:
        """."""

        model = models.InventoryInventoryItem
        fields = '__all__'


class InventoryRecordFilter(SearchComboboxBaseFilter):
    """Filter individual item inventory record."""

    class Meta:
        """Restrict filter fields."""

        model = models.InventoryRecord
        fields = '__all__'
