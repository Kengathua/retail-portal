"""Test transaction views."""

from django.test import Client
from django.urls import reverse

from rest_framework.test import APITestCase

from elites_franchise_portal.enterprises.models import Enterprise
from elites_franchise_portal.items.models import (
    Brand, BrandItemType, Category, Item, ItemModel, ItemType,
    ItemUnits, UnitsItemType, Units)
from elites_franchise_portal.debit.models import (
    Inventory, InventoryItem, InventoryRecord, InventoryInventoryItem)
from elites_franchise_portal.catalog.models import CatalogItem, Catalog, CatalogCatalogItem
from elites_franchise_portal.orders.models import (
    Cart, CartItem, Order, InstallmentsOrderItem)
from elites_franchise_portal.customers.models import Customer
from elites_franchise_portal.enterprise_mgt.models import EnterpriseSetupRule
from elites_franchise_portal.warehouses.models import Warehouse
from elites_franchise_portal.transactions.models import (
    Transaction, Payment, PaymentRequest)

from tests.utils.api import APITests

from model_bakery import baker
from model_bakery.recipe import Recipe

client= Client()


# class TestPaymentRequestView(APITests, APITestCase):
class TestPaymentRequestView(APITestCase):
    """."""

    def setUp(self):
        """."""
        enterprise = baker.make(
            Enterprise, reg_no='BS-9049444', name='Enterprise One',
            enterprise_code='EAL-E/EO-MB/2201-01', business_type='SHOP')
        enterprise_code = enterprise.enterprise_code
        payment = baker.make(
            Payment, account_number='+254718488252', required_amount='1',
            enterprise=enterprise_code)
        self.recipe = Recipe(
            PaymentRequest, service='M-PESA', payment_id=payment.id,
            business_account_number='600986', client_account_number='+254718488252',
            request_from_account_number='+254718488252', requested_amount=100,
            paid_amount=100, is_confirmed=True, auto_process_payment=True,
            enterprise=enterprise_code)

    url = 'v1:transactions:paymentrequest'


class TestMpesaCheckoutView(APITestCase):
    """."""

    def setUp(self) -> None:
        """."""
        enterprise = baker.make(Enterprise, name='Elites Age Supermarket')
        enterprise_code = enterprise.enterprise_code
        cat = baker.make(
            Category, category_name='Cat One',
            enterprise=enterprise_code)
        item_type = baker.make(
            ItemType, category=cat, type_name='Cooker',
            enterprise=enterprise_code)
        brand = baker.make(
            Brand, brand_name='Samsung', enterprise=enterprise_code)
        baker.make(
            BrandItemType, brand=brand, item_type=item_type,
            enterprise=enterprise_code)
        item_model = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731K-B SUT',
            enterprise=enterprise_code)
        item = baker.make(
            Item, item_model=item_model, barcode='83838388383', make_year=2020,
            enterprise=enterprise_code)
        s_units = baker.make(Units, units_name='5 Gas', enterprise=enterprise_code)
        baker.make(UnitsItemType, item_type=item_type, units=s_units, enterprise=enterprise_code)
        s_units.item_types.set([item_type])
        s_units.save()
        p_units = baker.make(Units, units_name='5 Gas', enterprise=enterprise_code)
        baker.make(UnitsItemType, item_type=item_type, units=p_units, enterprise=enterprise_code)
        p_units.item_types.set([item_type])
        p_units.save()
        baker.make(
            ItemUnits, item=item, sales_units=s_units, purchases_units=p_units,
            quantity_of_sale_units_per_purchase_unit=1, enterprise=enterprise_code)
        master_inventory = baker.make(
            Inventory, inventory_name='Elites Age Supermarket Working Stock Inventory',
            is_master=True, is_active=True, inventory_type='WORKING STOCK',
            enterprise=enterprise_code)
        available_inventory = baker.make(
            Inventory, inventory_name='Elites Age Supermarket Available Inventory',
            is_active=True, inventory_type='AVAILABLE', enterprise=enterprise_code)
        catalog = baker.make(
            Catalog, catalog_name='Elites Age Supermarket Standard Catalog',
            description='Standard Catalog', is_standard=True, enterprise=enterprise_code)
        receiving_warehouse = baker.make(
            Warehouse, warehouse_name='Elites Private Warehouse', is_default=True,
            enterprise=enterprise_code)
        baker.make(
            EnterpriseSetupRule, master_inventory=master_inventory,
            default_inventory=available_inventory, receiving_warehouse=receiving_warehouse,
            default_warehouse=receiving_warehouse, standard_catalog=catalog,
            default_catalog=catalog, is_active=True, enterprise=enterprise_code)
        inventory_item = baker.make(InventoryItem, item=item, enterprise=enterprise_code)
        baker.make(
            InventoryInventoryItem, inventory=available_inventory, inventory_item=inventory_item)
        baker.make(
            InventoryRecord, inventory=available_inventory, inventory_item=inventory_item,
            record_type='ADD', quantity_recorded=20, unit_price=350, enterprise=enterprise_code)
        catalog_item = baker.make(
            CatalogItem, inventory_item=inventory_item, enterprise=enterprise_code)
        customer = baker.make(
            Customer, customer_number=9876, first_name='John',
            last_name='Wick', other_names='Baba Yaga',
            phone_no='+254712345678', email='johnwick@parabellum.com')
        cart = baker.make(
            Cart, cart_code='EAS-C-10001', customer=customer, enterprise=enterprise_code)
        cart_item = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item, quantity_added=2,
            enterprise=enterprise_code)
        order = baker.make(Order, customer=customer, enterprise=enterprise_code)
        baker.make(
            InstallmentsOrderItem, order=order, cart_item=cart_item,
            confirmation_status='CONFIRMED',  enterprise=enterprise_code)
        self.transaction = baker.make(
            Transaction, transaction_code='#8765', transaction_type='DEPOSIT',
            customer=customer, amount=600, transaction_means='CASH',
            enterprise=enterprise_code)

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


class TestMpesaRegisterView(APITestCase):
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
