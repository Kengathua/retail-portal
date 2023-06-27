"""."""

from django.test import TestCase
from elites_retail_portal.enterprises.models import Enterprise
from elites_retail_portal.items.models import (
    Brand, BrandItemType, Category, Item, ItemModel, ItemType,
    ItemUnits, UnitsItemType, Units)
from elites_retail_portal.debit.models import (
    Inventory, InventoryItem, InventoryRecord, InventoryInventoryItem)
from elites_retail_portal.catalog.models import (
    CatalogItem, Catalog, CatalogCatalogItem)
from elites_retail_portal.orders.models import (
    Cart, CartItem, Order, InstantOrderItem, InstallmentsOrderItem,
    Installment)
from elites_retail_portal.customers.models import Customer
from elites_retail_portal.transactions.models import (
    Transaction, Payment, PaymentRequest)
from elites_retail_portal.warehouses.models import (
    Warehouse)

from model_bakery import baker
from model_bakery.recipe import Recipe


class TestTransaction(TestCase):
    """."""

    def test_create_cash_deposit_transaction(self):
        """."""
        franchise = baker.make(Enterprise, name='Elites Age Supermarket')
        enterprise_code = franchise.enterprise_code
        transaction = baker.make(
            Transaction, transaction_code='#8765', transaction_type='DEPOSIT',
            amount=2000, transaction_means='CASH', enterprise=enterprise_code)
        assert transaction
        assert Transaction.objects.count() == 1


class TestPayment(TestCase):
    """."""

    def test_make_payment(self):
        """."""
        franchise = baker.make(Enterprise, name='Elites Age Supermarket')
        enterprise_code = franchise.enterprise_code
        payment = baker.make(
            Payment, account_number='+254712345678', required_amount='1', enterprise=enterprise_code)

        assert payment
        assert Payment.objects.count() == 1


    def test_make_payment_request(self):
        """."""
        franchise = baker.make(Enterprise, name='Elites Age Supermarket')
        enterprise_code = franchise.enterprise_code
        payment = baker.make(
            Payment, account_number='+254712345678', required_amount='1',
            enterprise=enterprise_code)
        assert payment

        # payment.make_payment_request('M-PESA', None, '+254712345678', '174379')

        # assert PaymentRequest.objects.count() == 1
        # assert PaymentRequest.objects.all()[0].status == 'SUCCESS'


class TestPaymentRequest(TestCase):
    """."""

    def test_create_payment_request(self):
        """."""
        franchise = baker.make(Enterprise, name='Elites Age Supermarket')
        enterprise_code = franchise.enterprise_code
        payment = baker.make(
            Payment, account_number='+254718488252', required_amount='1',
            enterprise=enterprise_code)
        assert payment
        pass
        # payment_request = baker.make(
        #     PaymentRequest, service='M-PESA', payment_id=payment.id, business_account_number='600986',
        #     client_account_number='+254718488252', request_from_account_number='+254718488252',
        #     requested_amount=100, paid_amount=100, is_confirmed=True, auto_process_payment=True)

        # assert payment_request
        # assert PaymentRequest.objects.count() == 1

        # Transaction.objects.filter(payment_code=payment.payment_code).count() == 1
