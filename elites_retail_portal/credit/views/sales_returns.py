"""Purchases views file."""

from elites_retail_portal.common.views import BaseViewMixin
from elites_retail_portal.credit.models import SalesReturn
from elites_retail_portal.credit import serializers
from elites_retail_portal.credit import filters


class SalesReturnViewSet(BaseViewMixin):
    """SalesReturns view model."""

    queryset = SalesReturn.objects.all().order_by('-return_date')
    serializer_class = serializers.SalesReturnSerializer
    filterset_class = filters.SalesReturnFilter
    search_fields = (
        'sale_item__item_name', 'sale_item__item_code',)
