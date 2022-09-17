"""Filters file for Customer."""

from elites_franchise_portal.common.filters import SearchComboboxBaseFilter
from elites_franchise_portal.customers import models


class CustomerFilter(SearchComboboxBaseFilter):
    """Filter customers."""

    class Meta:
        """Restrict filter fields."""

        model = models.Customer
        fields = '__all__'
