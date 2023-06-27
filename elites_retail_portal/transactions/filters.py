"""Transaction filters file."""

from elites_retail_portal.common.filters import SearchComboboxBaseFilter
from elites_retail_portal.transactions import models


class PaymentFilter(SearchComboboxBaseFilter):
    """Filter payments."""

    class Meta:
        """Restrict filter fields."""

        model = models.Payment
        fields = '__all__'


class TransactionFilter(SearchComboboxBaseFilter):
    """Filter transactions."""

    class Meta:
        """Restrict filter fields."""

        model = models.Transaction
        fields = '__all__'
