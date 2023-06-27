"""Payment Gateway Tests file."""
# get_transaction_object sample data to mock
# callback_handler
from django.test import TestCase
from elites_retail_portal.transactions.helpers.payments.gateways import MpesaGateWay
from elites_retail_portal.transactions.models import (
    Transaction, Payment, PaymentRequest)
from elites_retail_portal.enterprises.models import Enterprise

from unittest.mock import patch

from model_bakery import baker
from model_bakery.recipe import Recipe

SAMPLE_CALLBACK_DATA = {
    'Body': {
        'stkCallback': {
            'MerchantRequestID': '7378-42053165-1',
            'CheckoutRequestID': 'ws_CO_23072022232346860718488252',
            'ResultCode': 0,
            'ResultDesc': 'The service request is processed successfully.',
            'CallbackMetadata': {
                'Item': [
                    {
                        'Name': 'Amount',
                        'Value': 1.0
                    },
                    {
                        'Name': 'MpesaReceiptNumber',
                        'Value': 'QGN4Z17OSE'
                    },
                    {
                        'Name': 'Balance'
                    },
                    {
                        'Name': 'TransactionDate',
                        'Value': 20230723232359
                    },
                    {
                        'Name': 'PhoneNumber',
                        'Value': 254712345678
                    }
                ]
            }
        }
    }
}


class TestMpesaGateway(TestCase):
    """."""

    def setUp(self) -> None:
        """."""
        self.checkout_request_id = SAMPLE_CALLBACK_DATA["Body"]["stkCallback"]["CheckoutRequestID"]
        pass

    def test_callback_handler(self):
        """."""
        mpesa_gateway = MpesaGateWay()
        franchise = baker.make(Enterprise, name='Elites Age Supermarket')
        enterprise_code = franchise.enterprise_code
        payment = baker.make(
            Payment, account_number='+254718488252', required_amount='1', enterprise=enterprise_code)
        payment_request = baker.make(
            PaymentRequest, payment_id=payment.id, requested_amount=1,
            request_from_account_number='254718488252',
            service='M-PESA', service_type='PAYBILL', client_account_number='174379',
            checkout_request_id=self.checkout_request_id, auto_process_payment=False,
            enterprise=enterprise_code)
        response = mpesa_gateway.callback_handler(SAMPLE_CALLBACK_DATA)

        assert response.data['status'] == 'ok'
        assert not payment_request.is_confirmed

        payment_request.refresh_from_db()
        assert payment_request.is_confirmed

    def test_get_payment_request_object(self):
        """."""
        mpesa_gateway = MpesaGateWay()
        franchise = baker.make(Enterprise, name='Elites Age Supermarket')
        enterprise_code = franchise.enterprise_code
        payment_request = baker.make(
            PaymentRequest, requested_amount=1, checkout_request_id=self.checkout_request_id,
            enterprise=enterprise_code)
        gateway_payment_request = mpesa_gateway.get_payment_request_object(SAMPLE_CALLBACK_DATA)

        assert gateway_payment_request == payment_request
