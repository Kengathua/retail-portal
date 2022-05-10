"""Debit side filters file."""
from elites_franchise_portal.common.filters import SearchComboboxBaseFilter
from elites_franchise_portal.debit import models


class StoreFilter(SearchComboboxBaseFilter):
    """Filter individual item store."""

    class Meta:
        """Restrict filter fields."""

        model = models.Store
        fields = '__all__'


class StoreRecordFilter(SearchComboboxBaseFilter):
    """Filter individual item store record."""

    class Meta:
        """Restrict filter fields."""

        model = models.StoreRecord
        fields = '__all__'


class InventoryItemFilter(SearchComboboxBaseFilter):
    """Filter individual item inventory item."""

    class Meta:
        """Restrict filter fields."""

        model = models.InventoryItem
        fields = '__all__'


class InventoryRecordFilter(SearchComboboxBaseFilter):
    """Filter individual item inventory record."""

    class Meta:
        """Restrict filter fields."""

        model = models.InventoryRecord
        fields = '__all__'
