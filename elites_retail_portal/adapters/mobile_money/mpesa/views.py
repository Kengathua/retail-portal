"""Mpesa Adapter views file."""

import json
import logging
import requests

from django.http import HttpResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import authentication_classes, permission_classes

from . import serializers
from django.conf import settings
from elites_retail_portal.transactions.helpers.payments.gateways import MpesaGateWay
from .models import MpesaAuthorization

mpesa_gateway = MpesaGateWay()


@authentication_classes([])
@permission_classes((AllowAny,))
class MpesaCheckout(APIView):
    """."""

    serializer = serializers.MpesaCheckoutSerializer

    def get(self, request):
        """."""
        return Response({"status": "OK"}, status=200)

    def post(self, request, *args, **kwargs):
        """."""
        data = request.data
        mpesa_authorization = MpesaAuthorization.objects.filter(
            enterprise=data['enterprise'])
        mpesa_authorization
        serializer = self.serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            payload = {"data": serializer.validated_data, "request": request}
            res = mpesa_gateway.stk_push_request(payload)
            return Response(res, status=200)


@authentication_classes([])
@permission_classes((AllowAny,))
class MpesaRegister(APIView):
    """."""

    def get(self, request):
        """."""
        return Response({"status": "OK"}, status=200)

    def post(self, request, *args, **kwargs):
        """."""
        api_url = "https://sandbox.safaricom.co.ke/mpesa/c2b/v1/registerurl"
        headers = {"Authorization": f"Bearer {mpesa_gateway.get_access_token()}"}
        options = {
            "ShortCode": '600426',
            "ResponseType": "Completed",
            "ConfirmationURL": f"{settings.NGROK_BASE_URL}/v1/adapters/mobile_money/safaricom/c2b/confirmation/",   # noqa
            "ValidationURL": f"{settings.NGROK_BASE_URL}/v1/adapters/mobile_money/safaricom/c2b/validation/",   # noqa
        }
        try:
            response = requests.post(api_url, json=options, headers=headers)
        except Exception:
            response = requests.post(api_url, json=options, headers=headers, verify=False)

        return HttpResponse(response.text)


@authentication_classes([])
@permission_classes((AllowAny,))
class MpesaCallBack(APIView):
    """."""

    def get(self, request):
        """."""
        return Response({"status": "OK"}, status=200)

    def post(self, request, *args, **kwargs):
        """."""
        logging.info("{}".format("Callback from MPESA"))
        data = request.body
        return mpesa_gateway.callback_handler(json.loads(data))


@authentication_classes([])
@permission_classes((AllowAny,))
class MpesaValidation(APIView):
    """."""

    def get(self, request):
        """."""
        context = {
            "ResultCode": 0,
            "ResultDesc": "Accepted"
        }
        return Response(context, status=200)

    def post(self, request):
        """."""
        return mpesa_gateway.validation(request)


@authentication_classes([])
@permission_classes((AllowAny,))
class MpesaConfirmation(APIView):
    """."""

    def get(self, request):
        """."""
        dict(request.data)
        mpesa_body = request.body.decode('utf-8')
        if mpesa_body:
            mpesa_payment = json.loads(mpesa_body)
            mpesa_payment
            # payment = MpesaPayment(
            #     first_name=mpesa_payment['FirstName'],
            #     last_name=mpesa_payment['LastName'],
            #     middle_name=mpesa_payment['MiddleName'],
            #     description=mpesa_payment['TransID'],
            #     phone_number=mpesa_payment['MSISDN'],
            #     amount=mpesa_payment['TransAmount'],
            #     reference=mpesa_payment['BillRefNumber'],
            #     organization_balance=mpesa_payment['OrgAccountBalance'],
            #     type=mpesa_payment['TransactionType'],
            # )
            # payment.save()
        context = {
            "ResultCode": 0,
            "ResultDesc": "Accepted"
        }
        return Response(context, status=200)
