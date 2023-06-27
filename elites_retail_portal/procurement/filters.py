"""Procurement filters file."""
import django_filters

from django.db import models

from elites_retail_portal.common.filters import SearchComboboxBaseFilter
from elites_retail_portal.procurement.models import (
    PurchaseOrderItem, PurchaseOrder, PurchaseOrderScan)


class PurchaseOrderFilter(SearchComboboxBaseFilter):
    """Filter individual purchase order."""

    class Meta:
        """Restrict filter fields."""

        model = PurchaseOrder
        fields = '__all__'


class PurchaseOrderScanFilter(SearchComboboxBaseFilter):
    """Filter individual purchase order."""

    class Meta:
        """Restrict filter fields."""

        model = PurchaseOrderScan
        fields = '__all__'
        filter_overrides = {
            models.FileField: {
                 'filter_class': django_filters.CharFilter,
                 'extra': lambda f: {
                     'lookup_expr': 'icontains',
                 },
            }
        }


class PurchaseOrderItemFilter(SearchComboboxBaseFilter):
    """Filter individual purchase order."""

    class Meta:
        """Restrict filter fields."""

        model = PurchaseOrderItem
        fields = '__all__'
