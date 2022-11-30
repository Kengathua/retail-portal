"""Tests for customers views."""

import uuid
from django.contrib.auth import get_user_model

from tests.utils import APITests
from elites_retail_portal.enterprises.models import Enterprise
from elites_retail_portal.customers.models import Customer

from rest_framework.test import APITestCase

from model_bakery import baker
from model_bakery.recipe import Recipe


class TestCustomerViewViewSet(APITests, APITestCase):
    """."""

    def setUp(self):
        """."""
        franchise = baker.make(
                Enterprise, name='Enterprise One', business_type='SUPERMARKET')
        enterprise_code = franchise.enterprise_code
        test_user = get_user_model().objects.create_superuser(
            email='testuser@email.com', first_name='Test', last_name='User',
            guid=uuid.uuid4(), password='Testpass254$', enterprise=enterprise_code)
        self.recipe = Recipe(
            Customer, customer_number=9876, first_name='John', last_name='Wick',
            other_names='Baba Yaga', phone_no='+254712345678', enterprise_user=test_user,
            email='johnwick@parabellum.com', enterprise=enterprise_code)
    url = 'v1:customers:customer'
