"""Customer models tests."""

import uuid
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from elites_retail_portal.customers.models import Customer
from elites_retail_portal.enterprises.models import Enterprise

from model_bakery import baker
from model_bakery.recipe import Recipe


class TestCustomer(TestCase):
    """."""

    def test_create_customer(self):
        """."""
        customer = baker.make(
            Customer, customer_number=9876, first_name='John', last_name='Wick', other_names='Baba Yaga',
            phone_no='+254712345678', email='johnwick@parabellum.com')

        assert customer
        assert customer.is_site == False
        assert Customer.objects.count() == 1

    def test_create_site_customer(self):
        """."""
        franchise = baker.make(
            Enterprise, name='Enterprise One', enterprise_code='EAL-E/EO-MB/2301-01',
            business_type='SHOP')
        enterprise_code = franchise.enterprise_code
        test_user = get_user_model().objects.create_superuser(
            email='testuser@email.com', first_name='Test', last_name='User',
            guid=uuid.uuid4(), password='Testpass254$', enterprise=enterprise_code)
        customer = baker.make(
            Customer, customer_number=9876, first_name='John', last_name='Wick',
            other_names='Baba Yaga', phone_no='+254712345678', enterprise_user=test_user,
            email='johnwick@parabellum.com', enterprise=enterprise_code)

        assert customer
        assert customer.is_site == True
        assert Customer.objects.count() == 1

    def test_fail_create_site_customer(self):
        """."""
        franchise = baker.make(
            Enterprise, name='Enterprise One', enterprise_code='EAL-E/EO-MB/2301-01',
            business_type='SHOP')
        enterprise_code = franchise.enterprise_code
        test_user = get_user_model().objects.create_superuser(
            email='testuser@email.com', first_name='Test', last_name='User',
            guid=uuid.uuid4(), password='Testpass254$', enterprise=enterprise_code)
        customer = Recipe(
            Customer, customer_number=9876, first_name='John', last_name='Wick',
            other_names='Baba Yaga', phone_no='+254712345678', is_site=True,
            email='johnwick@parabellum.com', enterprise=enterprise_code)

        with pytest.raises(ValidationError) as ve:
            customer.make()
        msg = 'Please assign a user to the customer'
        assert msg in ve.value.messages
