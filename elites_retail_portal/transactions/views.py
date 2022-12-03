"""Transaction views file."""

from elites_retail_portal.common.views import BaseViewMixin
from elites_retail_portal.transactions.models import (Transaction, Payment, PaymentRequest)
from elites_retail_portal.transactions import serializers


class TransactionViewSet(BaseViewMixin):
    """Transaction ViewSet class."""

    queryset = Transaction.objects.all().order_by('transaction_time')
    serializer_class = serializers.TransactionSerializer


class PaymentViewSet(BaseViewMixin):
    """Payment ViewSet class."""

    queryset = Payment.objects.all()
    serializer_class = serializers.PaymentSerializer

    # TODO Create an endpoint for making a payment requests
    # get response from the gateway


class PaymentRequestViewSet(BaseViewMixin):
    """Transaction ViewSet class."""

    queryset = PaymentRequest.objects.all()
    serializer_class = serializers.PaymentRequestSerializer
