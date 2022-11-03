"""Sales views  file."""

from elites_franchise_portal.debit.models import (
    Sale, SaleRecord)
from elites_franchise_portal.debit import serializers, filters
from elites_franchise_portal.common.views import BaseViewMixin

class SaleViewSet(BaseViewMixin):
    """Sale View class."""

    queryset = Sale.objects.all()
    serializer_class = serializers.SaleSerializer
    filterset_class = filters.SaleFilter
    search_fields = (
        'customer__first_name', 'customer__last_name',
        'customer__other_names', 'customer__customer_number',
        'order__order_number', 'sale_code',
    )

class SaleRecordViewSet(BaseViewMixin):
    """Sale Record view class."""

    queryset = SaleRecord.objects.all()
    serializer_class = serializers.SaleRecordSerializer
