"""Test transaction views."""

from django.test import TestCase, Client
from django.urls import reverse

from rest_framework.test import APITestCase

from elites_franchise_portal.franchises.models import Franchise
from elites_franchise_portal.items.models import (
    Brand, BrandItemType, Category, Item, ItemModel, ItemType,
    ItemUnits, UnitsItemType, Units)
from elites_franchise_portal.debit.models import (
    InventoryItem, InventoryRecord, Sale, SaleRecord,
    Warehouse, WarehouseItem, WarehouseWarehouseItem, WarehouseRecord)
from elites_franchise_portal.catalog.models import CatalogItem
from elites_franchise_portal.orders.models import (
    Cart, CartItem, Order, InstantOrderItem, InstallmentsOrderItem,
    Installment)
from elites_franchise_portal.customers.models import Customer
from elites_franchise_portal.transactions.models import (
    Transaction, Payment, PaymentRequest)

from tests.utils.api import APITests

from model_bakery import baker
from model_bakery.recipe import Recipe

client= Client()


class TestPaymentRequestView(APITests, APITestCase):
    """."""

    def setUp(self):
        """."""
        franchise = baker.make(
            Franchise, reg_no='BS-9049444', name='Franchise One',
            elites_code='EAL-F/FO-MB/2201-01', partnership_type='SHOP')
        franchise_code = franchise.elites_code
        payment = baker.make(
            Payment, account_number='+254712345678', required_amount='1',
            franchise=franchise_code)
        self.recipe = Recipe(
            PaymentRequest, service='M-PESA', payment_id=payment.id,
            business_account_number='600986', client_account_number='+254712345678',
            request_from_account_number='+254712345678', requested_amount=100,
            paid_amount=100, is_confirmed=True, auto_process_payment=True,
            franchise=franchise_code)

    url = 'v1:transactions:paymentrequest'


class TestMpesaCheckoutView(TestCase):
    """."""

    def setUp(self) -> None:
        """."""
        franchise = baker.make(Franchise, name='Elites Age Supermarket')
        franchise_code = franchise.elites_code
        cat = baker.make(
            Category, category_name='Cat One',
            franchise=franchise_code)
        item_type = baker.make(
            ItemType, category=cat, type_name='Cooker',
            franchise=franchise_code)
        brand = baker.make(
            Brand, brand_name='Samsung', franchise=franchise_code)
        baker.make(
            BrandItemType, brand=brand, item_type=item_type,
            franchise=franchise_code)
        item_model = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731K-B SUT',
            franchise=franchise_code)
        item = baker.make(
            Item, item_model=item_model, barcode='83838388383', make_year=2020,
            franchise=franchise_code)
        s_units = baker.make(Units, units_name='5 Gas', franchise=franchise_code)
        baker.make(UnitsItemType, item_type=item_type, units=s_units, franchise=franchise_code)
        s_units.item_types.set([item_type])
        s_units.save()
        p_units = baker.make(Units, units_name='5 Gas', franchise=franchise_code)
        baker.make(UnitsItemType, item_type=item_type, units=p_units, franchise=franchise_code)
        p_units.item_types.set([item_type])
        p_units.save()
        baker.make(
            ItemUnits, item=item, sales_units=s_units, purchases_units=p_units,
            items_per_purchase_unit=1, franchise=franchise_code)
        inventory_item = InventoryItem.objects.get(item=item, franchise=franchise_code)
        baker.make(
            InventoryRecord, inventory_item=inventory_item, record_type='ADD',
            quantity_recorded=20, unit_price=350, franchise=franchise_code)
        catalog_item = baker.make(
            CatalogItem, inventory_item=inventory_item, franchise=franchise_code)
        customer = baker.make(
            Customer, customer_number=9876, first_name='John',
            last_name='Wick', other_names='Baba Yaga',
            phone_no='+254712345678', email='johnwick@parabellum.com')
        cart = baker.make(
            Cart, cart_code='EAS-C-10001', customer=customer, franchise=franchise_code)
        cart_item = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item, quantity_added=2,
            franchise=franchise_code)
        order = baker.make(Order, customer=customer, franchise=franchise_code)
        baker.make(
            InstallmentsOrderItem, order=order, cart_item=cart_item,
            confirmation_status='CONFIRMED',  franchise=franchise_code)
        self.transaction = baker.make(
            Transaction, transaction_code='#8765', transaction_type='DEPOSIT',
            customer=customer, amount=600, transaction_means='CASH',
            franchise=franchise_code)

    url = 'v1:adapters:mobile_money:safaricom:c2b:checkout'

    def test_post(self):
        """."""
        from uuid import UUID
        from decimal import Decimal
        url = reverse(self.url)
        data = {
            'account_number': +254712345678,
            'phone_number': self.transaction.customer.phone_no,
            'amount': Decimal('1'),
            'balance': Decimal('1'),
            'created_by': UUID('bbda8fc1-9167-4aaf-9e35-42b34ff77470'),
            'customer_id': UUID('b19cdf64-9759-4a17-af21-c56ae13c388a'),
            'franchise': 'EAL-F/EAS-MB/2201-01',
            'reservation_amount': 0,
            'reservation_type': 'NO RESERVATION',
            'reserve_at': 'WALLET',
            'transaction_code': '#8765',
            'transaction_means': 'CASH',
            'transaction_processed': False,
            'transaction_type': 'DEPOSIT',
            'updated_by': UUID('61b88851-2322-4891-82ba-c9195d8d88b0'),
            'wallet_code': 23456789}

        resp = client.post(url, data)
        # assert resp.status_code == 200


class TestMpesaRegisterView(TestCase):
    """."""
    url = 'v1:adapters:mobile_money:safaricom:c2b:register'
    'v1:adapters:mobile_money:safaricom:c2b:confirmation'
    'v1:adapters:mobile_money:safaricom:c2b:confirmation'
    def test_post(self):
        """."""
        from uuid import UUID
        from decimal import Decimal
        url = reverse(self.url)
        url = 'v1/adapters/mobile_money/safaricom/c2b/register'
        data = {'LIPA_NA_MPESA_BUSINESS_SHORT_CODE':'600989'}
        resp = client.post(url, data)
        pass
