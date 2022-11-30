"""Sales views  file."""

from elites_retail_portal.debit.models import (
    Sale, SaleItem)
from elites_retail_portal.debit import serializers, filters
from elites_retail_portal.common.views import BaseViewMixin

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

class SaleItemViewSet(BaseViewMixin):
    """Sale Record view class."""

    queryset = SaleItem.objects.all()
    serializer_class = serializers.SaleItemSerializer
    filterset_class = filters.SaleItemFilter
    search_fields = (
        'catalog_item__inventory_item__item__item_name',
        'catalog_item__inventory_item__item__barcode',
        'sale__customer__full_name', 'processing_status',
        'sale_type', 'selling_price', 'total_amount', 'amount_paid'
    )
