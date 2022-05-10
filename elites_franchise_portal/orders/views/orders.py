"""Order views file."""

from elites_franchise_portal.common.views import BaseViewMixin
from elites_franchise_portal.orders.models import (
    Order, InstallmentsOrderItem, Installment,
    InstantOrderItem, OrderTransaction)
from elites_franchise_portal.orders import serializers


class OrderViewSet(BaseViewMixin):
    """Order viewset class."""

    queryset = Order.objects.all()
    serializer_class = serializers.OrderSerializer


class InstantOrderItemViewSet(BaseViewMixin):
    """Instant Order Item Viewset class."""

    queryset = InstantOrderItem.objects.all()
    serializer_class = serializers.InstantOrderItemSerializer


class InstallmentsOrderItemViewSet(BaseViewMixin):
    """Installment order item Viewset class."""

    queryset = InstallmentsOrderItem.objects.all()
    serializer_class = serializers.InstallmentsOrderItemSerializer


class InstallmentViewSet(BaseViewMixin):
    """Installment Viewset class."""

    queryset = Installment.objects.all().order_by('-installment_date')
    serializer_class = serializers.InstallmentSerializer


class OrderTransactionViewSet(BaseViewMixin):
    """Order Transactions Viewset class."""

    queryset = OrderTransaction.objects.all()
    serializer_class = serializers.OrderTransactionSerializer
