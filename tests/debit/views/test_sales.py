"""Sales tests file."""

import uuid
import pytest

from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase

from elites_retail_portal.debit.models import Sale
from elites_retail_portal.enterprises.models import Enterprise
from elites_retail_portal.customers.models import Customer

from tests.utils.api import APITests

from model_bakery import baker
from model_bakery.recipe import Recipe

pytestmark = pytest.mark.django_db


def test_get_cleaned_payload_data(data=None):
    """Clean data to remove module instance like UUID and Decimal."""
    if data:
        cleaned_data = {}
        for key, value in data.items():
            if not key == 'all_data':
                cleaned_data[key] = str(value) if value else None
        return cleaned_data


class TestSaleView(APITests, APITestCase):
    """."""

    def setUp(self):
        """."""
        franchise = baker.make(
            Enterprise, name='Enterprise One', business_type='SHOP')
        enterprise_code = franchise.enterprise_code
        test_user = get_user_model().objects.create_superuser(
            email='testuser@email.com', first_name='Test', last_name='User',
            guid=uuid.uuid4(), password='Testpass254$', enterprise=enterprise_code)
        self.customer = baker.make(
            Customer, customer_number=9876, first_name='John', last_name='Wick',
            is_enterprise=True, enterprise_user=test_user, phone_no='+254712345678',
            email='johnwick@parabellum.com', enterprise=enterprise_code)
        self.recipe = Recipe(
            Sale, customer=self.customer, enterprise=enterprise_code)

    url = 'v1:debit:sale'
