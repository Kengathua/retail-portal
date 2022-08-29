"""Sales views  file."""

from elites_franchise_portal.debit.models import (
    Sale, SaleRecord)
from elites_franchise_portal.debit import serializers
from elites_franchise_portal.common.views import BaseViewMixin

class SaleViewSet(BaseViewMixin):
    """Sale View class."""

    queryset = Sale.objects.all()
    serializer_class = serializers.SaleSerializer


class SaleRecordViewSet(BaseViewMixin):
    """Sale Record view class."""

    queryset = SaleRecord.objects.all()
    serializer_class = serializers.SaleRecordSerializer
