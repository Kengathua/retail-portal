"""Purchases views file."""

from elites_retail_portal.common.views import BaseViewMixin
from elites_retail_portal.credit.models import (
    Purchase, PurchaseItem, PurchasePayment)
from elites_retail_portal.credit import serializers
from elites_retail_portal.credit import filters


class PurchaseViewSet(BaseViewMixin):
    """Purchases view model."""

    queryset = Purchase.objects.all().order_by('-updated_on')
    serializer_class = serializers.PurchaseSerializer
    filterset_class = filters.PurchaseFilter
    search_fields = (
        'purchase_order__lpo_number',
        'supplier__enterprise__name', 'supplier__enterprise__enterprise_code',)


class PurchaseItemViewSet(BaseViewMixin):
    """Purchase Item view model."""

    queryset = PurchaseItem.objects.all().order_by('-updated_on')
    serializer_class = serializers.PurchaseItemSerializer
    filterset_class = filters.PurchaseItemFilter
    search_fields = ('item__item_name',)


class PurchasePaymentViewSet(BaseViewMixin):
    """Purchase Payment view model."""

    queryset = PurchasePayment.objects.all().order_by('-updated_on')
    serializer_class = serializers.PurchasePaymentSerializer
    filterset_class = filters.PurchasePaymentFilter
    search_fields = ('purchase__invoice_number',)
