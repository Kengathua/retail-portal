"""Sales views  file."""

from elites_retail_portal.debit.models import (
    PurchasesReturn)
from elites_retail_portal.debit import serializers, filters
from elites_retail_portal.common.views import BaseViewMixin


class PurchasesReturnViewSet(BaseViewMixin):
    """Purchases Returns View class."""

    queryset = PurchasesReturn.objects.all().order_by('-updated_on')
    serializer_class = serializers.PurchasesReturnSerializer
    filterset_class = filters.PurchasesReturnFilter
    search_fields = (
        'purchase_item__item__item_name', 'purchase_item__item__item_model__model_name',
        'purchase_item__item__item_model__model_code', 'purchase_item__item__barcode',
        'purchase_item__item__item_code', 'purchase_item__item__make_year',
    )
