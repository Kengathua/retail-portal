"""Debit side filters file."""

from elites_retail_portal.common.filters import SearchComboboxBaseFilter
from elites_retail_portal.credit import models


class PurchaseFilter(SearchComboboxBaseFilter):
    """Filter individual item store."""

    class Meta:
        """Restrict filter fields."""

        model = models.Purchase
        fields = '__all__'


class PurchaseItemFilter(SearchComboboxBaseFilter):
    """Filter Purchase Item."""

    class Meta:
        """Restrict filter fields."""

        model = models.PurchaseItem
        fields = '__all__'


class PurchasePaymentFilter(SearchComboboxBaseFilter):
    """Filter Purchase Payment."""

    class Meta:
        """Meta class for Purchase Payment filter."""

        model = models.PurchasePayment
        fields = '__all__'


class SalesReturnFilter(SearchComboboxBaseFilter):
    """Filter Sales Returns."""

    class Meta:
        """Meta class for Sales Returns filter."""

        model = models.SalesReturn
        fields = '__all__'
