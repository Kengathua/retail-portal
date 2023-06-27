"""Transaction views file."""

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from elites_retail_portal.common.views import BaseViewMixin
from elites_retail_portal.transactions.models import (Transaction, Payment, PaymentRequest)
from elites_retail_portal.transactions import serializers, filters
from elites_retail_portal.transactions.helpers.payments.reports import generate_payments_report


class TransactionViewSet(BaseViewMixin):
    """Transaction ViewSet class."""

    queryset = Transaction.objects.all().order_by('transaction_time')
    serializer_class = serializers.TransactionSerializer
    filterset_class = filters.TransactionFilter
    search_fields = (
        'transaction_code', 'payment_code', 'wallet_code',
        'account_number', 'balance', 'reservation_amount',
        'reservation_type', 'transaction_type', 'transaction_means',
        'customer__first_name', 'customer__last_name', 'customer__other_names')


class PaymentViewSet(BaseViewMixin):
    """Payment ViewSet class."""

    queryset = Payment.objects.all()
    serializer_class = serializers.PaymentSerializer
    filterset_class = filters.PaymentFilter
    search_fields = (
        'payment_code', 'transaction_code', 'account_number',
        'encounter__encounter_number', 'encounter__receipt_number',
        'required_amount', 'paid_amount', 'balance_amount',
        'final_amount', 'payment_method',
        'customer__first_name', 'customer__last_name', 'customer__other_names')
    # TODO Create an endpoint for making a payment requests
    # get response from the gateway

    @action(detail=False, methods=['post'])
    def generate_payments_report(self, request, *args, **kwargs):
        """Generate members upload template."""
        enterprise_code = self.request.user.enterprise
        start_date = self.request.data.get('start_date', None)
        end_date = self.request.data.get('end_date', None)

        data = generate_payments_report(enterprise_code, start_date, end_date)

        return Response(data=data, status=status.HTTP_201_CREATED)


class PaymentRequestViewSet(BaseViewMixin):
    """Transaction ViewSet class."""

    queryset = PaymentRequest.objects.all()
    serializer_class = serializers.PaymentRequestSerializer
