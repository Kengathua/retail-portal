"""Mpesa models test file."""

from django.test import TestCase

from model_bakery import baker
from elites_franchise_portal.adapters.mobile_money.mpesa.models import MpesaAuthorization


class TestMpesaAuthorization(TestCase):
    """."""

    def test_create_mpesa_authorization(self):
        mpesa_authorization = baker.make(
            MpesaAuthorization, consumer_key='0uLw9wagDGvENbgRObMdu7dEX4Ex636m',
            consumer_secret='gLiDGxDwiyhhcuBL',
            pass_key='bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919')

        assert mpesa_authorization
        assert MpesaAuthorization.objects.count() == 1
