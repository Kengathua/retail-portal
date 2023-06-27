"""Procurement views file."""

from django.utils import timezone

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser, MultiPartParser

from elites_retail_portal.common.views import BaseViewMixin
from elites_retail_portal.procurement.models import (
    PurchaseOrder, PurchaseOrderItem, PurchaseOrderScan)
from elites_retail_portal.procurement import serializers, filters
from elites_retail_portal.credit.serializers import PurchaseSerializer
from elites_retail_portal.credit.models import Purchase


class PurchaseOrderViewSet(BaseViewMixin):
    """PurchaseOrder ViewSet class."""

    queryset = PurchaseOrder.objects.all().order_by('-lpo_date')
    serializer_class = serializers.PurchaseOrderSerializer
    filterset_class = filters.PurchaseOrderFilter
    parser_classes = (MultiPartParser, JSONParser)
    search_fields = (
        'lpo_number', 'supplier__name', 'description', 'authorized_by__first_name',
        'authorized_by__last_name', 'authorized_by__other_names',
        'authorized_by__staff_number')

    @action(methods=['post'], detail=True)
    def create_purchase(self, request, *args, **kwargs):
        """Create purchase."""
        purchase_order = self.get_object()
        payload = {
            'created_by': self.request.user.id,
            'updated_by': self.request.user.id,
            'enterprise': self.request.user.enterprise,
            'purchase_order': purchase_order,
            'supplier': purchase_order.supplier,
            'purchase_date': self.request.data.get('purchase_date', None) or timezone.now(),
            'invoice_number': self.request.data.get('invoice_number', None),
        }
        purchase = Purchase.objects.create(**payload)
        serializer = PurchaseSerializer(purchase)

        return Response(data=serializer.data, status=status.HTTP_201_CREATED)


class PurchaseOrderScanViewSet(BaseViewMixin):
    """PurchaseOrder Scan ViewSet class."""

    queryset = PurchaseOrderScan.objects.all().order_by('-created_on')
    serializer_class = serializers.PurchaseOrderScanSerializer
    filterset_class = filters.PurchaseOrderScanFilter
    parser_classes = (MultiPartParser, JSONParser)
    search_fields = ('purchase_order__lpo_number',)


class PurchaseOrderItemViewSet(BaseViewMixin):
    """PurchaseOrderItem ViewSet class."""

    queryset = PurchaseOrderItem.objects.all().order_by('-created_on')
    serializer_class = serializers.PurchaseOrderItemSerializer
    filterset_class = filters.PurchaseOrderItemFilter
