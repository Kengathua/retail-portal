"""."""

from django.test import TestCase
from elites_franchise_portal.franchises.models import Franchise
from elites_franchise_portal.items.models import (
    Brand, BrandItemType, Category, Item, ItemModel, ItemType,
    ItemUnits, UnitsItemType, Units)
from elites_franchise_portal.debit.models import (
    InventoryItem, InventoryRecord, Sale, SaleRecord,
    Store, StoreRecord)
from elites_franchise_portal.catalog.models import CatalogItem
from elites_franchise_portal.orders.models import (
    Cart, CartItem, Order, InstantOrderItem, InstallmentsOrderItem,
    Installment)
from elites_franchise_portal.customers.models import Customer
from elites_franchise_portal.transactions.models import (
    Transaction, Payment, PaymentRequest)

from model_bakery import baker
from model_bakery.recipe import Recipe


class TestTransaction(TestCase):
    """."""

    def test_create_cash_deposit_transaction(self):
        """."""
        franchise = baker.make(Franchise, name='Elites Age Supermarket')
        franchise_code = franchise.elites_code
        transaction = baker.make(
            Transaction, transaction_code='#8765', transaction_type='DEPOSIT',
            amount=2000, transaction_means='CASH', franchise=franchise_code)
        assert transaction
        assert Transaction.objects.count() == 1

    def test_process_transaction_clear_instant_order_item(self):
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
        brand_item_type = baker.make(
            BrandItemType, brand=brand, item_type=item_type,
            franchise=franchise_code)
        item_model = baker.make(
            ItemModel, brand_item_type=brand_item_type, model_name='GE731K-B SUT',
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
        inventory_item = baker.make(
            InventoryItem, item=item, franchise=franchise_code)
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
        instant_order_item = baker.make(
            InstantOrderItem, order=order, franchise=franchise.elites_code,
            cart_item=cart_item, confirmation_status='CONFIRMED', amount_paid=350)
        transaction = baker.make(
            Transaction, transaction_code='#8765', transaction_type='DEPOSIT',
            customer=customer, amount=2000, transaction_means='CASH',
            franchise=franchise_code)
        assert instant_order_item.is_cleared == False   # noqa
        instant_order_item.refresh_from_db()
        transaction.refresh_from_db()
        assert instant_order_item.is_cleared == True   # noqa
        assert transaction.balance == 1300

    def test_process_transaction_clear_few_instant_order_item(self):
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
        brand_item_type = baker.make(
            BrandItemType, brand=brand, item_type=item_type,
            franchise=franchise_code)
        item_model = baker.make(
            ItemModel, brand_item_type=brand_item_type, model_name='GE731K-B SUT',
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
        inventory_item = baker.make(
            InventoryItem, item=item, franchise=franchise_code)
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
        instant_order_item = baker.make(
            InstantOrderItem, order=order, franchise=franchise.elites_code,
            cart_item=cart_item, confirmation_status='CONFIRMED', amount_paid=350)
        transaction = baker.make(
            Transaction, transaction_code='#8765', transaction_type='DEPOSIT',
            customer=customer, amount=500, transaction_means='CASH',
            franchise=franchise_code)

        assert transaction
        assert Transaction.objects.count() == 1
        instant_order_item.refresh_from_db()
        assert instant_order_item.is_cleared == False   # noqa
        assert instant_order_item.no_of_items_cleared == 1
        assert instant_order_item.no_of_items_awaiting_clearance == 1

    def test_process_transaction_clear_installment_order_items(self):
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
        brand_item_type = baker.make(
            BrandItemType, brand=brand, item_type=item_type,
            franchise=franchise_code)
        item_model = baker.make(
            ItemModel, brand_item_type=brand_item_type, model_name='GE731K-B SUT',
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
        inventory_item = baker.make(
            InventoryItem, item=item, franchise=franchise_code)
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
        installment_order_item = baker.make(
            InstallmentsOrderItem, franchise=franchise.elites_code,
            order=order, cart_item=cart_item,  confirmation_status='CONFIRMED')
        transaction = baker.make(
            Transaction, transaction_code='#8765', transaction_type='DEPOSIT',
            customer=customer, amount=2000, transaction_means='CASH',
            franchise=franchise_code)
        assert transaction
        assert installment_order_item.amount_paid == 0  # noqa
        assert installment_order_item.deposit_amount == 0  # noqa

        installment_order_item.refresh_from_db()
        assert installment_order_item.amount_paid == 700  # noqa
        assert installment_order_item.deposit_amount == 0
        assert installment_order_item.amount_due == 0

    def test_process_transaction_as_an_installment(self):
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
        brand_item_type = baker.make(
            BrandItemType, brand=brand, item_type=item_type,
            franchise=franchise_code)
        item_model = baker.make(
            ItemModel, brand_item_type=brand_item_type, model_name='GE731K-B SUT',
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
        inventory_item = baker.make(
            InventoryItem, item=item, franchise=franchise_code)
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
        installment_order_item = baker.make(
            InstallmentsOrderItem, deposit_amount=150, amount_paid=150, order=order,
            cart_item=cart_item, confirmation_status='CONFIRMED', franchise=franchise_code)
        transaction = baker.make(
            Transaction, transaction_code='#8765', transaction_type='DEPOSIT',
            customer=customer, amount=200, transaction_means='CASH',
            franchise=franchise_code)

        assert transaction
        assert installment_order_item

        assert installment_order_item.amount_paid == 150
        installment_order_item.refresh_from_db()
        assert installment_order_item.amount_paid == 350
        assert installment_order_item.total_amount == 700
        assert installment_order_item.amount_due == 350

    def test_process_transaction_installment_order_item_deposit(self):
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
        brand_item_type = baker.make(
            BrandItemType, brand=brand, item_type=item_type,
            franchise=franchise_code)
        item_model = baker.make(
            ItemModel, brand_item_type=brand_item_type, model_name='GE731K-B SUT',
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
        inventory_item = baker.make(
            InventoryItem, item=item, franchise=franchise_code)
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
        installment_order_item = baker.make(
            InstallmentsOrderItem, order=order, cart_item=cart_item,
            confirmation_status='CONFIRMED',  franchise=franchise_code)
        transaction = baker.make(
            Transaction, transaction_code='#8765', transaction_type='DEPOSIT',
            customer=customer, amount=600, transaction_means='CASH',
            franchise=franchise_code)
        assert transaction
        assert installment_order_item.amount_paid == 0  # noqa
        assert installment_order_item.deposit_amount == 0  # noqa
        assert installment_order_item.amount_due == 700 # noqa

        installment_order_item.refresh_from_db()
        assert installment_order_item.amount_paid == 600  # noqa
        assert installment_order_item.deposit_amount == 600 # noqa
        assert installment_order_item.amount_due == 100 # noqa

    def test_clear_item_using_transaction_to_installment(self):
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
        brand_item_type = baker.make(
            BrandItemType, brand=brand, item_type=item_type,
            franchise=franchise_code)
        item_model = baker.make(
            ItemModel, brand_item_type=brand_item_type, model_name='GE731K-B SUT',
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
        inventory_item = baker.make(
            InventoryItem, item=item, franchise=franchise_code)
        baker.make(
            InventoryRecord, inventory_item=inventory_item, record_type='ADD',
            quantity_recorded=20, unit_price=350, franchise=franchise_code)
        catalog_item = baker.make(
            CatalogItem, inventory_item=inventory_item, franchise=franchise_code)
        customer = baker.make(
            Customer, customer_number=9876, first_name='John', last_name='Wick',
            other_names='Baba Yaga', phone_no='+254712345678',
            email='johnwick@parabellum.com', franchise=franchise_code)
        cart = baker.make(
            Cart, cart_code='EAS-C-10001', customer=customer, franchise=franchise_code)
        cart_item = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item, quantity_added=2,
            franchise=franchise_code)
        order = baker.make(Order, customer=customer, franchise=franchise_code)
        installment_order_item = baker.make(
            InstallmentsOrderItem, order=order, cart_item=cart_item, deposit_amount=150,
            amount_paid=150, confirmation_status='CONFIRMED',  franchise=franchise_code)
        transaction = baker.make(
            Transaction, transaction_code='#8765', transaction_type='DEPOSIT',
            customer=customer, amount=600, transaction_means='CASH',
            franchise=franchise_code)

        assert Installment.objects.count() == 1
        assert installment_order_item
        assert transaction

        installments = Installment.objects.filter(installment_item__order=order)
        assert installments.count() == 1
        installment = installments.first()
        assert installment
        assert installment.amount == 550

        transaction.balance == 600
        transaction.refresh_from_db()
        transaction.balance == 50

    def test_create_mpesa_paybill_deposit_transaction(self):
        """."""
        MPESA_PAYBILL = 'MPESA PAYBILL'
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
        brand_item_type = baker.make(
            BrandItemType, brand=brand, item_type=item_type,
            franchise=franchise_code)
        item_model1 = baker.make(
            ItemModel, brand_item_type=brand_item_type, model_name='RT26HAR2DSA',
            franchise=franchise_code)
        item_model2 = baker.make(
            ItemModel, brand_item_type=brand_item_type, model_name='HSHHSHS8837',
            franchise=franchise_code)
        item1 = baker.make(
            Item, item_model=item_model1, barcode='9876543', make_year=2020,
            create_inventory_item=False, franchise=franchise_code)
        item2 = baker.make(
            Item, item_model=item_model2, barcode='23456789', make_year=2020,
            create_inventory_item=False, franchise=franchise_code)
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
        inventory_item1 = baker.make(InventoryItem, item=item1, franchise=franchise_code)
        inventory_item2 = baker.make(InventoryItem, item=item2, franchise=franchise_code)
        baker.make(
            InventoryRecord, inventory_item=inventory_item1, record_type='ADD',
            quantity_recorded=15, unit_price=300, franchise=franchise_code)
        baker.make(
            InventoryRecord, inventory_item=inventory_item2, record_type='ADD',
            quantity_recorded=10, unit_price=300, franchise=franchise_code)
        catalog_item1 = baker.make(
            CatalogItem, inventory_item=inventory_item1, franchise=franchise_code)
        baker.make(
            CatalogItem, inventory_item=inventory_item2, franchise=franchise_code)
        customer = baker.make(
            Customer, customer_number=9876, first_name='John', last_name='Wick',
            other_names='Baba Yaga', phone_no='+254712345678', account_number=65434598765,
            email='johnwick@parabellum.com', franchise=franchise_code)
        cart = baker.make(Cart, customer=customer)
        cart_item1 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item1, quantity_added=2,
            order_now=True, franchise=franchise_code)
        cart_item2 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item1, quantity_added=1,
            order_now=True, is_installment=True, franchise=franchise_code)
        order = baker.make(Order, customer=customer, franchise=franchise_code)
        installment_order_item = baker.make(
            InstallmentsOrderItem, order=order, cart_item=cart_item1, deposit_amount=150,
            amount_paid=150, confirmation_status='CONFIRMED',  franchise=franchise_code)
        instant_order_item = baker.make(
            InstantOrderItem, order=order, franchise=franchise_code, cart_item=cart_item2,
            confirmation_status='CONFIRMED')
        transaction = baker.make(
            Transaction, transaction_code='#8765', transaction_type='DEPOSIT',
            account_number=customer.account_number, amount=2000, transaction_means=MPESA_PAYBILL,
            franchise=franchise_code)

        assert order
        assert instant_order_item
        assert installment_order_item
        assert transaction
        transaction.refresh_from_db()
        assert transaction.balance == 1100


class TestPayment(TestCase):
    """."""

    def test_make_payment(self):
        """."""
        franchise = baker.make(Franchise, name='Elites Age Supermarket')
        franchise_code = franchise.elites_code
        payment = baker.make(
            Payment, account_number='+254712345678', required_amount='1', franchise=franchise_code)

        assert payment
        assert Payment.objects.count() == 1


    def test_make_payment_request(self):
        """."""
        franchise = baker.make(Franchise, name='Elites Age Supermarket')
        franchise_code = franchise.elites_code
        payment = baker.make(
            Payment, account_number='+254712345678', required_amount='1',
            franchise=franchise_code)
        payment.make_payment_request('M-PESA', None, '+254712345678', '174379')

        assert PaymentRequest.objects.count() == 1
        assert PaymentRequest.objects.all()[0].status == 'SUCCESS'


class TestPaymentRequest(TestCase):
    """."""

    def test_create_payment_request(self):
        """."""
        franchise = baker.make(Franchise, name='Elites Age Supermarket')
        franchise_code = franchise.elites_code
        payment = baker.make(
            Payment, account_number='+254712345678', required_amount='1',
            franchise=franchise_code)
        payment_request = baker.make(
            PaymentRequest, service='M-PESA', payment_id=payment.id, business_account_number='600986',
            client_account_number='+254712345678', request_from_account_number='+254712345678',
            requested_amount=100, paid_amount=100, is_confirmed=True, auto_process_payment=True)

        assert payment_request
        assert PaymentRequest.objects.count() == 1

        Transaction.objects.filter(payment_code=payment.payment_code).count() == 1
