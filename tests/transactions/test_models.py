"""."""

from django.test import TestCase
from elites_franchise_portal.enterprises.models import Enterprise
from elites_franchise_portal.items.models import (
    Brand, BrandItemType, Category, Item, ItemModel, ItemType,
    ItemUnits, UnitsItemType, Units)
from elites_franchise_portal.debit.models import (
    Inventory, InventoryItem, InventoryRecord, InventoryInventoryItem)
from elites_franchise_portal.catalog.models import (
    CatalogItem, Catalog, CatalogCatalogItem)
from elites_franchise_portal.orders.models import (
    Cart, CartItem, Order, InstantOrderItem, InstallmentsOrderItem,
    Installment)
from elites_franchise_portal.customers.models import Customer
from elites_franchise_portal.transactions.models import (
    Transaction, Payment, PaymentRequest)
from elites_franchise_portal.enterprise_mgt.models import EnterpriseSetupRule
from elites_franchise_portal.warehouses.models import (
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

    def test_process_transaction_clear_instant_order_item(self):
        """."""
        franchise = baker.make(Enterprise, name='Elites Age Supermarket')
        enterprise_code = franchise.enterprise_code
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
        baker.make(
            CatalogCatalogItem, catalog=catalog, catalog_item=catalog_item, enterprise=enterprise_code)
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
        instant_order_item = baker.make(
            InstantOrderItem, order=order, enterprise=franchise.enterprise_code,
            cart_item=cart_item, confirmation_status='CONFIRMED', amount_paid=350)
        transaction = baker.make(
            Transaction, transaction_code='#8765', transaction_type='DEPOSIT',
            customer=customer, amount=2000, transaction_means='CASH',
            enterprise=enterprise_code)
        assert instant_order_item.is_cleared == False   # noqa
        instant_order_item.refresh_from_db()
        transaction.refresh_from_db()
        assert instant_order_item.is_cleared == True   # noqa
        assert transaction.balance == 1300

    def test_process_transaction_clear_few_instant_order_item(self):
        """."""
        franchise = baker.make(Enterprise, name='Elites Age Supermarket')
        enterprise_code = franchise.enterprise_code
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
            InventoryRecord, inventory=available_inventory, inventory_item=inventory_item, record_type='ADD',
            quantity_recorded=20, unit_price=350, enterprise=enterprise_code)
        catalog_item = baker.make(
            CatalogItem, inventory_item=inventory_item, enterprise=enterprise_code)
        baker.make(
            CatalogCatalogItem, catalog=catalog, catalog_item=catalog_item, enterprise=enterprise_code)
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
        instant_order_item = baker.make(
            InstantOrderItem, order=order, enterprise=franchise.enterprise_code,
            cart_item=cart_item, confirmation_status='CONFIRMED', amount_paid=0)
        transaction = baker.make(
            Transaction, transaction_code='#8765', transaction_type='DEPOSIT',
            customer=customer, amount=500, transaction_means='CASH',
            enterprise=enterprise_code)

        assert transaction
        assert Transaction.objects.count() == 1
        instant_order_item.refresh_from_db()
        assert instant_order_item.is_cleared == False   # noqa
        assert instant_order_item.quantity_cleared == 1
        assert instant_order_item.quantity_awaiting_clearance == 1

    def test_process_transaction_clear_installment_order_items(self):
        """."""
        franchise = baker.make(Enterprise, name='Elites Age Supermarket')
        enterprise_code = franchise.enterprise_code
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
        installment_order_item = baker.make(
            InstallmentsOrderItem, enterprise=franchise.enterprise_code,
            order=order, cart_item=cart_item,  confirmation_status='CONFIRMED')
        transaction = baker.make(
            Transaction, transaction_code='#8765', transaction_type='DEPOSIT',
            customer=customer, amount=2000, transaction_means='CASH',
            enterprise=enterprise_code)
        assert transaction
        assert installment_order_item.amount_paid == 0  # noqa
        assert installment_order_item.deposit_amount == 0  # noqa

        installment_order_item.refresh_from_db()
        assert installment_order_item.amount_paid == 700  # noqa
        assert installment_order_item.deposit_amount == 0
        assert installment_order_item.amount_due == 0

    def test_process_transaction_as_an_installment(self):
        """."""
        franchise = baker.make(Enterprise, name='Elites Age Supermarket')
        enterprise_code = franchise.enterprise_code
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
        installment_order_item = baker.make(
            InstallmentsOrderItem, deposit_amount=150, amount_paid=150, order=order,
            cart_item=cart_item, confirmation_status='CONFIRMED', enterprise=enterprise_code)
        transaction = baker.make(
            Transaction, transaction_code='#8765', transaction_type='DEPOSIT',
            customer=customer, amount=200, transaction_means='CASH',
            enterprise=enterprise_code)

        assert transaction
        assert installment_order_item

        assert installment_order_item.amount_paid == 150
        installment_order_item.refresh_from_db()
        assert installment_order_item.amount_paid == 350
        assert installment_order_item.total_amount == 700
        assert installment_order_item.amount_due == 350

    def test_process_transaction_installment_order_item_deposit(self):
        """."""
        franchise = baker.make(Enterprise, name='Elites Age Supermarket')
        enterprise_code = franchise.enterprise_code
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
        installment_order_item = baker.make(
            InstallmentsOrderItem, order=order, cart_item=cart_item,
            confirmation_status='CONFIRMED',  enterprise=enterprise_code)
        transaction = baker.make(
            Transaction, transaction_code='#8765', transaction_type='DEPOSIT',
            customer=customer, amount=600, transaction_means='CASH',
            enterprise=enterprise_code)
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
        franchise = baker.make(Enterprise, name='Elites Age Supermarket')
        enterprise_code = franchise.enterprise_code
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
            Customer, customer_number=9876, first_name='John', last_name='Wick',
            other_names='Baba Yaga', phone_no='+254712345678',
            email='johnwick@parabellum.com', enterprise=enterprise_code)
        cart = baker.make(
            Cart, cart_code='EAS-C-10001', customer=customer, enterprise=enterprise_code)
        cart_item = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item, quantity_added=2,
            enterprise=enterprise_code)
        order = baker.make(Order, customer=customer, enterprise=enterprise_code)
        installment_order_item = baker.make(
            InstallmentsOrderItem, order=order, cart_item=cart_item, deposit_amount=150,
            amount_paid=150, confirmation_status='CONFIRMED',  enterprise=enterprise_code)
        transaction = baker.make(
            Transaction, transaction_code='#8765', transaction_type='DEPOSIT',
            customer=customer, amount=600, transaction_means='CASH',
            enterprise=enterprise_code)

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
        franchise = baker.make(Enterprise, name='Elites Age Supermarket')
        enterprise_code = franchise.enterprise_code
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
        item_model1 = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='RT26HAR2DSA',
            enterprise=enterprise_code)
        item_model2 = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='HSHHSHS8837',
            enterprise=enterprise_code)
        item1 = baker.make(
            Item, item_model=item_model1, barcode='9876543', make_year=2020,
            enterprise=enterprise_code)
        item2 = baker.make(
            Item, item_model=item_model2, barcode='23456789', make_year=2020,
            enterprise=enterprise_code)
        s_units = baker.make(Units, units_name='packet', enterprise=enterprise_code)
        baker.make(UnitsItemType, item_type=item_type, units=s_units, enterprise=enterprise_code)
        s_units.item_types.set([item_type])
        s_units.save()
        p_units = baker.make(Units, units_name='Dozen', enterprise=enterprise_code)
        baker.make(UnitsItemType, item_type=item_type, units=p_units, enterprise=enterprise_code)
        p_units.item_types.set([item_type])
        p_units.save()
        baker.make(
            ItemUnits, item=item1, sales_units=s_units, purchases_units=p_units,
            quantity_of_sale_units_per_purchase_unit=12, enterprise=enterprise_code)
        baker.make(
            ItemUnits, item=item2, sales_units=s_units, purchases_units=p_units,
            quantity_of_sale_units_per_purchase_unit=12, enterprise=enterprise_code)
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
        inventory_item1 = baker.make(
            InventoryItem, item=item1, enterprise=enterprise_code)
        inventory_item2 = baker.make(
            InventoryItem, item=item2, enterprise=enterprise_code)
        baker.make(
            InventoryInventoryItem, inventory=available_inventory, inventory_item=inventory_item1)
        baker.make(
            InventoryInventoryItem, inventory=available_inventory, inventory_item=inventory_item2)
        baker.make(
            InventoryRecord,  inventory=available_inventory, inventory_item=inventory_item1,
            record_type='ADD', quantity_recorded=15, unit_price=300, enterprise=enterprise_code)
        baker.make(
            InventoryRecord,  inventory=available_inventory, inventory_item=inventory_item2,
            record_type='ADD', quantity_recorded=10, unit_price=300, enterprise=enterprise_code)
        catalog_item1 = baker.make(
            CatalogItem, inventory_item=inventory_item1, enterprise=enterprise_code)
        catalog_item2 = baker.make(
            CatalogItem, inventory_item=inventory_item2, enterprise=enterprise_code)
        baker.make(CatalogCatalogItem, catalog=catalog, catalog_item=catalog_item1)
        baker.make(CatalogCatalogItem, catalog=catalog, catalog_item=catalog_item2)
        customer = baker.make(
            Customer, customer_number=9876, first_name='John', last_name='Wick',
            other_names='Baba Yaga', phone_no='+254712345678', account_number=65434598765,
            email='johnwick@parabellum.com', enterprise=enterprise_code)
        cart = baker.make(Cart, customer=customer)
        cart_item1 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item1, quantity_added=2,
            order_now=True, enterprise=enterprise_code)
        cart_item2 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item1, quantity_added=1,
            order_now=True, is_installment=True, enterprise=enterprise_code)
        order = baker.make(Order, customer=customer, enterprise=enterprise_code)
        installment_order_item = baker.make(
            InstallmentsOrderItem, order=order, cart_item=cart_item1, deposit_amount=150,
            amount_paid=150, confirmation_status='CONFIRMED',  enterprise=enterprise_code)
        instant_order_item = baker.make(
            InstantOrderItem, order=order, enterprise=enterprise_code, cart_item=cart_item2,
            confirmation_status='CONFIRMED')
        transaction = baker.make(
            Transaction, transaction_code='#8765', transaction_type='DEPOSIT',
            account_number=customer.account_number, amount=2000, transaction_means=MPESA_PAYBILL,
            enterprise=enterprise_code)

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
