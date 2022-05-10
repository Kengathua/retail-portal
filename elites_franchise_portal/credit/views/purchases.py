"""Purchases views file."""

from elites_franchise_portal.common.views import BaseViewMixin
from elites_franchise_portal.credit.models import Purchase
from elites_franchise_portal.credit import serializers


class PurchaseViewSet(BaseViewMixin):
    """Purchases view model."""

    queryset = Purchase.objects.all()
    serializer_class = serializers.PurchaseSerializer
