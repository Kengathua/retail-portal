"""Debit side filters file."""

import django_filters

from elites_franchise_portal.common.filters import SearchComboboxBaseFilter
from elites_franchise_portal.debit import models
from elites_franchise_portal.encounters.filters import EncounterFilter

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


class PurchasesReturnFilter(SearchComboboxBaseFilter):
    """Filter Purchases Returns."""

    class Meta:
        """Purchases Return Filter Meta class."""

        model = models.PurchasesReturn
        fields = '__all__'


class SaleFilter(SearchComboboxBaseFilter):
    """Filter sale."""

    class Meta:
        """Restrict filter fields."""

        model = models.Sale
        fields = '__all__'

    @classmethod
    def filter_for_lookup(cls, f, lookup_type):
        # override date range lookups
        from django.db import models
        if isinstance(f, models.JSONField) and lookup_type == 'exact':
            return django_filters.CharFilter, {}

        # use default behavior otherwise
        return super().filter_for_lookup(f, lookup_type)

class SaleItemFilter(SearchComboboxBaseFilter):
    """Filter sale item."""

    class Meta:
        """Restrict filter fields."""

        model = models.SaleItem
        fields = '__all__'
