"""Tests for customers views."""

import uuid
from django.contrib.auth import get_user_model

from tests.utils import APITests
from elites_franchise_portal.franchises.models import Franchise
from elites_franchise_portal.customers.models import Customer

from rest_framework.test import APITestCase

from model_bakery import baker
from model_bakery.recipe import Recipe


class TestCustomerViewViewSet(APITests, APITestCase):
    """."""

    def setUp(self):
        """."""
        franchise = baker.make(
                Franchise, name='Franchise One', partnership_type='SUPERMARKET')
        franchise_code = franchise.elites_code
        test_user = get_user_model().objects.create_superuser(
            email='testuser@email.com', first_name='Test', last_name='User',
            guid=uuid.uuid4(), password='Testpass254$', franchise=franchise_code)
        self.recipe = Recipe(
            Customer, customer_number=9876, first_name='John', last_name='Wick',
            other_names='Baba Yaga', phone_no='+254712345678', franchise_user=test_user,
            email='johnwick@parabellum.com', franchise=franchise_code)
    url = 'v1:customers:customer'
