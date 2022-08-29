"""Sales tests file."""

import uuid
import json
import pytest

from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase

from elites_franchise_portal.items.models import (
    Brand, BrandItemType, Category, Item, ItemModel, ItemType,
    ItemUnits, UnitsItemType, Units)
from elites_franchise_portal.debit.models import (
    Inventory, InventoryItem, InventoryInventoryItem,
    InventoryRecord, Sale, SaleRecord)
from elites_franchise_portal.debit.models import (
    Warehouse)
from elites_franchise_portal.orders.models import (
    Cart, CartItem, Order, InstantOrderItem, InstallmentsOrderItem,
    Installment, OrderTransaction)
from elites_franchise_portal.transactions.models import Transaction, Payment
from elites_franchise_portal.franchises.models import Franchise
from elites_franchise_portal.customers.models import Customer
from elites_franchise_portal.catalog.models import (
    Catalog, CatalogItem)
from elites_franchise_portal.catalog.serializers import (
    CatalogItemSerializer)
from elites_franchise_portal.transactions.models import (
    Transaction, Payment)
from elites_franchise_portal.customers.serializers import CustomerSerializer
from tests.utils.login_mixins import authenticate_test_user

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
            Franchise, name='Franchise One', partnership_type='SHOP')
        franchise_code = franchise.elites_code
        test_user = get_user_model().objects.create_superuser(
            email='testuser@email.com', first_name='Test', last_name='User',
            guid=uuid.uuid4(), password='Testpass254$', franchise=franchise_code)
        self.customer = baker.make(
            Customer, customer_number=9876, first_name='John', last_name='Wick',
            is_franchise=True, franchise_user=test_user, phone_no='+254712345678',
            email='johnwick@parabellum.com', franchise=franchise_code)
        self.recipe = Recipe(
            Sale, customer=self.customer, franchise=franchise_code)

    url = 'v1:debit:sale'
