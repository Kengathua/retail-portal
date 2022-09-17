"""Purchases views file."""

from elites_franchise_portal.common.views import BaseViewMixin
from elites_franchise_portal.credit.models import Purchase
from elites_franchise_portal.credit import serializers
from elites_franchise_portal.credit import filters

class PurchaseViewSet(BaseViewMixin):
    """Purchases view model."""

    queryset = Purchase.objects.all()
    serializer_class = serializers.PurchaseSerializer
    filterset_class = filters.PurchaseFilter
    search_fields = (
        'supplier__enterprise__name', 'supplier__enterprise__enterprise_code',
        'item__item_name')
