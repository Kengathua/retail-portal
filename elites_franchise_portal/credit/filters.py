"""Debit side filters file."""

from elites_franchise_portal.common.filters import SearchComboboxBaseFilter
from elites_franchise_portal.credit import models


class PurchaseFilter(SearchComboboxBaseFilter):
    """Filter individual item store."""

    class Meta:
        """Restrict filter fields."""

        model = models.Purchase
        fields = '__all__'
