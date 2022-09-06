"""Payments utils file."""

import time
import math
import base64
import logging
from datetime import datetime
from urllib import request
import requests

from django.http import HttpResponse, JsonResponse
from requests.auth import HTTPBasicAuth
from rest_framework.response import Response
from phonenumber_field.phonenumber import PhoneNumber
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.exceptions import ValidationError

from phonenumber_field.phonenumber import to_python
from phonenumbers.phonenumberutil import is_possible_number

from elites_franchise_portal.transactions.models import Transaction, PaymentRequest
from elites_franchise_portal.transactions import serializers
from .utils import PaymentErrorCode

logging = logging.getLogger("default")


# TODO Register callback and verification url

class MpesaGateWay:
    """Mpesa Gateway class."""

    shortcode = None
    consumer_key = None
    consumer_secret = None
    access_token_url = None
    access_token = None
    access_token_expiration = None
    checkout_url = None
    timestamp = None

    def __init__(self):
        """Initialize variables."""
        self.now = datetime.now()
        self.shortcode = '174379'
        self.consumer_key = '0uLw9wagDGvENbgRObMdu7dEX4Ex636m'
        self.consumer_secret = 'gLiDGxDwiyhhcuBL'
        self.pass_key = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
        self.access_token_url = settings.MPESA_ACCESS_TOKEN_URL
        self.LIPA_NA_MPESA_BUSINESS_SHORT_CODE = '600982'

        self.password = self.generate_password()
        self.c2b_callback = settings.MPESA_C2B_URL
        self.checkout_url = settings.MPESA_CHECKOUT_URL
        self.base_url = settings.NGROK_BASE_URL

        try:
            self.access_token = self.get_access_token()
            if self.access_token is None:
                raise Exception("Request for access token failed.")
        except Exception as e:
            logging.error("Error {}".format(e))
        else:
            self.access_token_expiration = time.time() + 3400

        # simulation = self.simulate_c2b_transaction()
        # registration1 = self.register_urls1()
        # registration2 = self.register_urls2()
        # import pdb
        # pdb.set_trace()

    def get_access_token(self):
        """Get access token."""
        try:
            res = requests.get(
                self.access_token_url,
                auth=HTTPBasicAuth(self.consumer_key, self.consumer_secret),
            )
            token = res.json()["access_token"]
            self.headers = {"Authorization": "Bearer %s" % token}
        except Exception as err:
            logging.error("Error {}".format(err))
            raise err
        else:
            token = res.json()["access_token"]
            self.headers = {"Authorization": "Bearer %s" % token}
            return token

    class Decorators:
        """Mpesa Gateway decorator class."""

        @staticmethod
        def refreshToken(decorated):
            """Refresh the access token."""
            def wrapper(gateway, *args, **kwargs):
                if (
                    gateway.access_token_expiration
                    and time.time() > gateway.access_token_expiration
                ):
                    token = gateway.get_access_token()
                    gateway.access_token = token
                return decorated(gateway, *args, **kwargs)

            return wrapper

    def generate_password(self, shortcode=None, pass_key=None):
        """Generate mpesa api password using the provided shortcode and passkey."""
        if not shortcode:
            shortcode = self.shortcode
        if not pass_key:
            pass_key = self.pass_key
        self.timestamp = self.now.strftime("%Y%m%d%H%M%S")
        password_str = shortcode + pass_key + self.timestamp
        password_bytes = password_str.encode("ascii")
        return base64.b64encode(password_bytes).decode("utf-8")

    def validate_possible_number(self, phone, country=None):
        """Validate a possible phone number."""
        phone_number = to_python(phone, country)
        if (
            phone_number
            and not is_possible_number(phone_number)
            or not phone_number.is_valid()
        ):
            raise ValidationError(
                "The phone number entered is not valid.", code=PaymentErrorCode.INVALID
            )
        return phone_number

    def validate_phone_number(self, phone_number):
        """Remove the preciding + or replace the 0 with 254."""
        phone_number = str(phone_number)
        if phone_number[0] == "+":
            phone_number = phone_number[1:]
        if phone_number[0] == "0":
            phone_number = "254" + phone_number[1:]
        try:
            self.validate_possible_number(phone_number, "KE")
        except ValidationError:
            raise serializers.ValidationError({"error": "Phone number is not valid"})

        return phone_number

    @Decorators.refreshToken
    def stk_push_request(self, payload):
        """Push the notification on the client's phone."""
        request = None
        STK_PUSH_URL = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
        try:
            shortcode = payload['BusinessShortCode']
            pass_key = payload['PassKey']
            password = self.generate_password(shortcode, pass_key)
        except KeyError:
            password = self.generate_password()
            payload['BusinessShortCode'] = '174379'
            request = payload['request']
            data = request.data
            payload['Amount'] = data['amount']
            payload['PartyA'] = '600426'
            payload['PartyB'] = 174379
            payload['PhoneNumber'] = self.validate_phone_number('254712345678')

        phone_number = self.validate_phone_number(payload['PhoneNumber'])

        req_data = {
            "BusinessShortCode": payload['BusinessShortCode'],
            "Password": password,
            "Timestamp": self.timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": math.ceil(float(payload['Amount'])),
            "PartyA": payload['PartyA'],
            "PartyB": payload['PartyB'],
            "PhoneNumber": phone_number,
            "CallBackURL": self.c2b_callback,
            "AccountReference": "Test",
            "TransactionDesc": "Test",
        }

        import pdb
        pdb.set_trace()

        res = requests.post(
            STK_PUSH_URL, json=req_data, headers=self.headers, timeout=30
        )
        status_code = res.status_code
        res_data = res.json()
        logging.info("Mpesa request data {}".format(req_data))
        logging.info("Mpesa response info {}".format(res_data))

        if res.ok and request:
            payload["ip"] = request.META.get("REMOTE_ADDR")
            payload["checkout_request_id"] = res_data["CheckoutRequestID"]
            import pdb
            pdb.set_trace()

        return status_code, res_data

    def check_status(self, data):
        """Check transaction status."""
        try:
            status = data["Body"]["stkCallback"]["ResultCode"]
        except Exception as e:
            logging.error(f"Error: {e}")
            status = 1
        return status

    def get_payment_request_object(self, data):
        """Get the transaction oblect."""
        checkout_request_id = data["Body"]["stkCallback"]["CheckoutRequestID"]
        payment_request = None
        payment_requests = PaymentRequest.objects.filter(
            checkout_request_id=checkout_request_id
        )

        if payment_requests.exists and payment_requests.count() == 1:
            payment_request = payment_requests.first()

        return payment_request

    def process_successful_payment(self, data, payment_request):
        """Process a successful payment."""
        items = data["Body"]["stkCallback"]["CallbackMetadata"]["Item"]
        for item in items:
            if item["Name"] == "Amount":
                amount = item["Value"]
            elif item["Name"] == "MpesaReceiptNumber":
                receipt_no = item["Value"]
            elif item["Name"] == "PhoneNumber":
                phone_number = item["Value"]

        payment_request_updates = {
            'paid_amount': amount,
            'phone_number': phone_number,
            'receipt_no': receipt_no,
            'is_confirmed': True,
        }

        payment_request._meta.model.objects.filter(id=payment_request.id).update(**payment_request_updates)
        payment_request.refresh_from_db()

        return payment_request

    def callback_handler(self, data):
        """Handle callback."""
        status = self.check_status(data)
        payment_request = self.get_payment_request_object(data)
        if payment_request:
            if status == 0:
                self.process_successful_payment(data, payment_request)
            else:
                payment_request.status = 1

            payment_request_data = serializers.PaymentRequestSerializer(payment_request).data

            logging.info("Transaction completed info {}".format(payment_request_data))

            return Response({"status": "ok", "code": 0}, status=200)

        # TODO Return an error message for this
        return Response({"status": "ok", "code": 0}, status=200)

    def validation(self, request):
        """."""
        context = {
            "ResultCode": 0,
            "ResultDesc": "Accepted"
        }
        return JsonResponse(dict(context))

    @csrf_exempt
    def register_urls1(self):
        """."""
        api_url = "https://sandbox.safaricom.co.ke/mpesa/c2b/v1/registerurl"
        headers = {"Authorization": f"Bearer {self.get_access_token()}"}
        options = {
            "ShortCode": '600426',
            "ResponseType": "Completed",
            "ValidationURL": f"{self.base_url}/v1/adapters/mobile_money/safaricom/c2b/validation/",
            "ConfirmationURL": f"{self.base_url}/v1/adapters/mobile_money/safaricom/c2b/confirmation/",    # noqa
        }
        response = requests.post(api_url, json=options, headers=headers)
        import pdb
        pdb.set_trace()
        # response = requests.post(api_url, json=options, headers=headers, verify=False)

        return HttpResponse(response.text)

    def register_urls2(self):
        """."""
        my_access_token = self.get_access_token()

        api_url = "https://sandbox.safaricom.co.ke/safaricom/c2b/v1/registerurl"

        headers = {"Authorization": "Bearer %s" % my_access_token}

        payload = {
            "ShortCode": self.LIPA_NA_MPESA_BUSINESS_SHORT_CODE,
            "ResponseType": "Completed",
            "ConfirmationURL": f"{self.base_url}/api/payments/c2b-confirmation/",
            "ValidationURL":   f"{self.base_url}/api/payments/c2b-validation/",
        }

        response = requests.post(api_url, json=payload, headers=headers)
        # response = requests.post(api_url, json=request, headers=headers, verify=False)

    def simulate_c2b_transaction(self):
        my_access_token = self.get_access_token()

        api_url = "https://sandbox.safaricom.co.ke/safaricom/c2b/v1/simulate"

        headers = {"Authorization": f"Bearer {my_access_token}"}

        payload = {
            "ShortCode": self.LIPA_NA_MPESA_BUSINESS_SHORT_CODE,
            "CommandID": "CustomerPayBillOnline",
            "Amount": "20",
            "Msisdn": +254708374149,
            "BillRefNumber": "+254718488252",
        }

        response = requests.post(api_url, json=payload, headers=headers)

        import pdb
        pdb.set_trace()
        # response = requests.post(api_url, json=request, headers=headers, verify=False)

        print(response.text)
