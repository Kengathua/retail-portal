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
    InventoryItem, InventoryRecord, Sale, SaleRecord)
from elites_franchise_portal.orders.models import (
    Cart, CartItem, Order, InstantOrderItem, InstallmentsOrderItem)
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

    def test_new_sale(self):
        """."""
        self.client = authenticate_test_user()
        sale = self.recipe.make()
        franchise_code = sale.franchise
        #   TODO Create a catalog item and Serialize it
        cat = baker.make(
            Category, category_name='Cat One',
            franchise=franchise_code)
        item_type = baker.make(
            ItemType, category=cat, type_name='Cooker',
            franchise=franchise_code)
        brand = baker.make(
            Brand, brand_name='Samsung', franchise=franchise_code)
        brand_item_type = baker.make(
            BrandItemType, brand=brand, item_type=item_type,
            franchise=franchise_code)
        item_model1 = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731K-B SUT',
            franchise=franchise_code)
        item_model2 = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='WRTHY46-G DAT',
            franchise=franchise_code)
        item1 = baker.make(
            Item, item_model=item_model1, barcode='83838388383', make_year=2020,
            franchise=franchise_code, create_inventory_item=False)
        item2 = baker.make(
            Item, item_model=item_model2, barcode='83838388383', make_year=2020,
            franchise=franchise_code, create_inventory_item=False)
        s_units = baker.make(Units, units_name='packet', franchise=franchise_code)
        baker.make(UnitsItemType, item_type=item_type, units=s_units, franchise=franchise_code)
        s_units.item_types.set([item_type])
        s_units.save()
        p_units = baker.make(Units, units_name='Dozen', franchise=franchise_code)
        baker.make(UnitsItemType, item_type=item_type, units=p_units, franchise=franchise_code)
        p_units.item_types.set([item_type])
        p_units.save()
        baker.make(
            ItemUnits, item=item1, sales_units=s_units, purchases_units=p_units,
            items_per_purchase_unit=12, franchise=franchise_code)
        baker.make(
            ItemUnits, item=item2, sales_units=s_units, purchases_units=p_units,
            items_per_purchase_unit=12, franchise=franchise_code)
        inventory_item1 = baker.make(
            InventoryItem, item=item1, franchise=franchise_code)
        inventory_item2 = baker.make(
            InventoryItem, item=item2, franchise=franchise_code)
        baker.make(
            InventoryRecord, inventory_item=inventory_item1, record_type='ADD',
            quantity_recorded=20, unit_price=1500,
            franchise=franchise_code)
        baker.make(
            InventoryRecord, inventory_item=inventory_item2, record_type='ADD',
            quantity_recorded=20, unit_price=2000,
            franchise=franchise_code)
        baker.make(
            Catalog, name='Elites Age Supermarket Standard Catalog',
            description='Standard Catalog', is_standard_catalog=True,
            franchise=franchise_code)
        catalog_item1 = baker.make(
            CatalogItem, inventory_item=inventory_item1, franchise=franchise_code)
        catalog_item2 = baker.make(
            CatalogItem, inventory_item=inventory_item2, franchise=franchise_code)
        customer_serializer = CustomerSerializer(self.customer)
        billing = [
            {
                'catalog_item': str(catalog_item1.id),
                'item_name': catalog_item1.inventory_item.item.item_name,
                'quantity': 2,
                'unit_price': 1600,
                'total': 3200,
                'sale_type': 'INSTANT'
            },
            {
                'catalog_item': str(catalog_item2.id),
                'item_name': catalog_item2.inventory_item.item.item_name,
                'quantity': 3,
                'unit_price': 2200,
                'total': 6600,
                'sale_type': 'INSTALLMENT'
            },
        ]
        payment = {'means': 'CASH', 'amount': 5000, }

        customer_data = test_get_cleaned_payload_data(customer_serializer.data)

        encounter = {
            'customer': str(self.customer.id),
            'billing': billing,
            'payments': [payment],
        }
        encounter = json.loads(json.dumps(encounter))
        url = reverse(self.url + '-new-sale', kwargs={'pk': sale.id})

        # resp = self.client.post(url, encounter)
        resp = self.client.post(url, encounter, format='json')
        record1 = SaleRecord.objects.filter(sale_type='INSTANT').first()
        record2 = SaleRecord.objects.filter(sale_type='INSTALLMENT').first()

        assert set([row['id'] for row in resp.data]).issuperset({str(record1.id), str(record2.id)})

        assert SaleRecord.objects.count() == 2
        assert Cart.objects.count() == 1
        assert CartItem.objects.count() == 2
        assert CartItem.objects.filter(is_installment=False).count() == 1
        assert CartItem.objects.filter(is_installment=True).count() == 1
        assert Order.objects.count() == 1
        assert InstantOrderItem.objects.count() == 1
        assert InstallmentsOrderItem.objects.count() == 1
        assert Transaction.objects.count() == 1
        assert Payment.objects.count() == 1

        instant_item = InstantOrderItem.objects.first()
        assert instant_item.is_cleared
        assert instant_item.no_of_items_awaiting_clearance == 0
        assert instant_item.no_of_items_cleared == 2
        assert instant_item.payment_status == 'PAID'
        assert instant_item.amount_paid == 3200

        installment_item = InstallmentsOrderItem.objects.first()
        assert installment_item.deposit_amount == 1800
        assert installment_item.amount_due == 4800
