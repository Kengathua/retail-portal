"""."""

import pytest
from unittest import mock
from django.test import TestCase
from django.core.exceptions import ValidationError

from elites_franchise_portal.enterprises.models import Enterprise
from elites_franchise_portal.items.models import (
    Brand, BrandItemType, Category, Item, ItemModel, ItemType,
    ItemUnits, UnitsItemType, Units)
from elites_franchise_portal.debit.models import (
    InventoryItem, Inventory, InventoryInventoryItem, InventoryRecord,
    Sale, SaleRecord)
from elites_franchise_portal.catalog.models import (
    Section, Catalog, CatalogItem, CatalogCatalogItem)
from elites_franchise_portal.orders.models import (
    Cart, CartItem, Order, OrderTransaction, InstantOrderItem)
from elites_franchise_portal.customers.models import Customer
from elites_franchise_portal.warehouses.models import (
    Warehouse, WarehouseItem, WarehouseRecord, WarehouseWarehouseItem)
from elites_franchise_portal.credit.models import Purchase
from elites_franchise_portal.encounters.models import Encounter
from elites_franchise_portal.encounters.tasks import process_customer_encounter
from elites_franchise_portal.transactions.models import (
    Transaction, Payment, PaymentRequest)

from model_bakery import baker
from model_bakery.recipe import Recipe


class TestSection(TestCase):
    """."""

    def test_create_section(self):
        """."""
        franchise = baker.make(Enterprise, name='Franchise Number One')
        sec = baker.make(
            Section, section_name='Section A', enterprise=franchise.enterprise_code)

        assert sec
        assert sec.section_code == 'FNO-MB/S-SA/2201'
        assert Section.objects.count() == 1


class TestCatalog(TestCase):
    """."""

    def test_create_catalog(self):
        """."""
        franchise = baker.make(Enterprise, name='Elites Age Supermarket')
        enterprise_code = franchise.enterprise_code
        catalog = baker.make(
            Catalog, catalog_name='Elites Age Supermarket Standard Catalog',
            description='Standard Catalog', is_standard=True, enterprise=enterprise_code)
        assert catalog
        assert Catalog.objects.count() == 1


class TestCatalogItem(TestCase):
    """."""

    def test_create_catalog_item(self):
        """."""
        franchise = baker.make(Enterprise, name='Elites Age Supermarket')
        enterprise_code = franchise.enterprise_code
        cat = baker.make(
            Category, category_name='ELECTRONICS',
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
        s_units = baker.make(Units, units_name='packet', enterprise=enterprise_code)
        baker.make(UnitsItemType, item_type=item_type, units=s_units, enterprise=enterprise_code)
        s_units.item_types.set([item_type])
        s_units.save()
        p_units = baker.make(Units, units_name='Dozen', enterprise=enterprise_code)
        baker.make(UnitsItemType, item_type=item_type, units=p_units, enterprise=enterprise_code)
        p_units.item_types.set([item_type])
        p_units.save()
        baker.make(
            ItemUnits, item=item, sales_units=s_units, purchases_units=p_units,
            quantity_of_sale_units_per_purchase_unit=12, enterprise=enterprise_code)
        master_inventory = baker.make(
            Inventory, inventory_name='Elites Age Supermarket Working Stock Inventory',
            is_master=True, is_active=True, inventory_type='WORKING STOCK',
            enterprise=enterprise_code)
        available_inventory = baker.make(
            Inventory, inventory_name='Elites Age Supermarket Available Inventory',
            is_active=True, inventory_type='AVAILABLE', enterprise=enterprise_code)
        inventory_item = baker.make(InventoryItem, item=item, enterprise=enterprise_code)
        baker.make(
            InventoryInventoryItem, inventory=master_inventory, inventory_item=inventory_item)
        baker.make(
            InventoryInventoryItem, inventory=available_inventory, inventory_item=inventory_item)
        catalog_item = baker.make(
            CatalogItem, inventory_item=inventory_item, enterprise=enterprise_code)

        assert catalog_item
        assert CatalogItem.objects.count() == 1

    def test_fail_create_catalog_item_exists(self):
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
        s_units = baker.make(Units, units_name='packet', enterprise=enterprise_code)
        baker.make(UnitsItemType, item_type=item_type, units=s_units, enterprise=enterprise_code)
        s_units.item_types.set([item_type])
        s_units.save()
        p_units = baker.make(Units, units_name='Dozen', enterprise=enterprise_code)
        baker.make(UnitsItemType, item_type=item_type, units=p_units, enterprise=enterprise_code)
        p_units.item_types.set([item_type])
        p_units.save()
        baker.make(
            ItemUnits, item=item, sales_units=s_units, purchases_units=p_units,
            quantity_of_sale_units_per_purchase_unit=12, enterprise=enterprise_code)
        master_inventory = baker.make(
            Inventory, inventory_name='Elites Age Supermarket Working Stock Inventory',
            is_master=True, is_active=True, inventory_type='WORKING STOCK',
            enterprise=enterprise_code)
        available_inventory = baker.make(
            Inventory, inventory_name='Elites Age Supermarket Available Inventory',
            is_active=True, inventory_type='AVAILABLE', enterprise=enterprise_code)
        inventory_item = baker.make(InventoryItem, item=item, enterprise=enterprise_code)
        baker.make(
            InventoryInventoryItem, inventory=master_inventory, inventory_item=inventory_item)
        baker.make(
            InventoryInventoryItem, inventory=available_inventory, inventory_item=inventory_item)
        catalog_item = baker.make(
            CatalogItem, inventory_item=inventory_item, enterprise=enterprise_code)
        catalog_item_recipe = Recipe(
            CatalogItem, inventory_item=inventory_item, enterprise=enterprise_code)

        with pytest.raises(ValidationError) as ve:
            catalog_item_recipe.make()
        msg_dict = {'inventory_item': ['Catalog item with this Inventory item already exists.']}
        assert ve.value.message_dict == msg_dict

        assert catalog_item
        assert CatalogItem.objects.count() == 1

    def test_add_catalog_item_to_cart(self):
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
        s_units = baker.make(Units, units_name='packet', enterprise=enterprise_code)
        baker.make(UnitsItemType, item_type=item_type, units=s_units, enterprise=enterprise_code)
        s_units.item_types.set([item_type])
        s_units.save()
        p_units = baker.make(Units, units_name='Dozen', enterprise=enterprise_code)
        baker.make(UnitsItemType, item_type=item_type, units=p_units, enterprise=enterprise_code)
        p_units.item_types.set([item_type])
        p_units.save()
        baker.make(
            ItemUnits, item=item, sales_units=s_units, purchases_units=p_units,
            quantity_of_sale_units_per_purchase_unit=12, enterprise=enterprise_code)
        master_inventory = baker.make(
            Inventory, inventory_name='Elites Age Supermarket Working Stock Inventory',
            is_master=True, is_active=True, inventory_type='WORKING STOCK',
            enterprise=enterprise_code)
        available_inventory = baker.make(
            Inventory, inventory_name='Elites Age Supermarket Available Inventory',
            is_active=True, inventory_type='AVAILABLE', enterprise=enterprise_code)
        inventory_item = baker.make(InventoryItem, item=item, enterprise=enterprise_code)
        baker.make(
            InventoryInventoryItem, inventory=master_inventory, inventory_item=inventory_item)
        baker.make(
            InventoryInventoryItem, inventory=available_inventory, inventory_item=inventory_item)
        catalog_item = baker.make(
            CatalogItem, inventory_item=inventory_item, enterprise=enterprise_code)
        customer = baker.make(
            Customer, customer_number=9876, first_name='John', last_name='Wick',
            phone_no='+254712345678', email='johnwick@parabellum.com')
        catalog_item.add_to_cart(customer)
        assert Cart.objects.count() == 1
        assert CartItem.objects.count() == 1

    def test_add_item_to_cart_specify_quantity(self):
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
        s_units = baker.make(Units, units_name='packet', enterprise=enterprise_code)
        baker.make(UnitsItemType, item_type=item_type, units=s_units, enterprise=enterprise_code)
        s_units.item_types.set([item_type])
        s_units.save()
        p_units = baker.make(Units, units_name='Dozen', enterprise=enterprise_code)
        baker.make(UnitsItemType, item_type=item_type, units=p_units, enterprise=enterprise_code)
        p_units.item_types.set([item_type])
        p_units.save()
        baker.make(
            ItemUnits, item=item, sales_units=s_units, purchases_units=p_units,
            quantity_of_sale_units_per_purchase_unit=12, enterprise=enterprise_code)
        master_inventory = baker.make(
            Inventory, inventory_name='Elites Age Supermarket Working Stock Inventory',
            is_master=True, is_active=True, inventory_type='WORKING STOCK',
            enterprise=enterprise_code)
        available_inventory = baker.make(
            Inventory, inventory_name='Elites Age Supermarket Available Inventory',
            is_active=True, inventory_type='AVAILABLE', enterprise=enterprise_code)
        inventory_item = baker.make(InventoryItem, item=item, enterprise=enterprise_code)
        baker.make(
            InventoryInventoryItem, inventory=master_inventory, inventory_item=inventory_item)
        baker.make(
            InventoryInventoryItem, inventory=available_inventory, inventory_item=inventory_item)
        catalog_item = baker.make(
            CatalogItem, inventory_item=inventory_item, enterprise=enterprise_code)
        customer = baker.make(
            Customer, customer_number=9876, first_name='John', last_name='Wick',
            phone_no='+254712345678', email='johnwick@parabellum.com')
        catalog_item.add_to_cart(customer, 2)
        assert Cart.objects.count() == 1
        assert CartItem.objects.count() == 1

        cart_item = CartItem.objects.get(catalog_item__inventory_item=inventory_item)
        cart_item.opening_quantity == 0
        cart_item.quantity_added == 2
        cart_item.closing_quantity == 2

    def test_add_item_to_cart_multiple_times(self):
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
        s_units = baker.make(Units, units_name='packet', enterprise=enterprise_code)
        baker.make(UnitsItemType, item_type=item_type, units=s_units, enterprise=enterprise_code)
        s_units.item_types.set([item_type])
        s_units.save()
        p_units = baker.make(Units, units_name='Dozen', enterprise=enterprise_code)
        baker.make(UnitsItemType, item_type=item_type, units=p_units, enterprise=enterprise_code)
        p_units.item_types.set([item_type])
        p_units.save()
        baker.make(
            ItemUnits, item=item, sales_units=s_units, purchases_units=p_units,
            quantity_of_sale_units_per_purchase_unit=12, enterprise=enterprise_code)
        master_inventory = baker.make(
            Inventory, inventory_name='Elites Age Supermarket Working Stock Inventory',
            is_master=True, is_active=True, inventory_type='WORKING STOCK',
            enterprise=enterprise_code)
        available_inventory = baker.make(
            Inventory, inventory_name='Elites Age Supermarket Available Inventory',
            is_active=True, inventory_type='AVAILABLE', enterprise=enterprise_code)
        inventory_item = baker.make(InventoryItem, item=item, enterprise=enterprise_code)
        baker.make(
            InventoryInventoryItem, inventory=master_inventory, inventory_item=inventory_item)
        baker.make(
            InventoryInventoryItem, inventory=available_inventory, inventory_item=inventory_item)
        catalog_item = baker.make(
            CatalogItem, inventory_item=inventory_item, enterprise=enterprise_code)
        customer = baker.make(
            Customer, customer_number=9876, first_name='John', last_name='Wick',
            phone_no='+254712345678', email='johnwick@parabellum.com')
        catalog_item.add_to_cart(customer)
        assert Cart.objects.count() == 1
        assert CartItem.objects.count() == 1
        cart_item = CartItem.objects.get(catalog_item__inventory_item=inventory_item)

        assert cart_item.opening_quantity == 0
        assert cart_item.quantity_added == 1
        assert cart_item.closing_quantity == 1
        assert not cart_item.is_installment
        assert not cart_item.order_now

        catalog_item.add_to_cart(customer)
        cart_item.refresh_from_db()
        assert cart_item.opening_quantity == 1
        assert cart_item.quantity_added == 1
        assert cart_item.closing_quantity == 2
        assert not cart_item.is_installment
        assert not cart_item.order_now

        catalog_item.add_to_cart(customer)
        cart_item.refresh_from_db()
        assert cart_item.opening_quantity == 2
        assert cart_item.quantity_added == 1
        assert cart_item.closing_quantity == 3
        assert not cart_item.is_installment
        assert not cart_item.order_now

        catalog_item.add_to_cart(customer, None, 5)
        cart_item.refresh_from_db()
        assert cart_item.opening_quantity == 3
        assert cart_item.quantity_added == 5
        assert cart_item.closing_quantity == 8
        assert not cart_item.is_installment
        assert not cart_item.order_now

        catalog_item.add_to_cart(customer, None, 2)
        cart_item.refresh_from_db()
        assert cart_item.opening_quantity == 8
        assert cart_item.quantity_added == 2
        assert cart_item.closing_quantity == 10
        assert not cart_item.is_installment
        assert not cart_item.order_now

        catalog_item.add_to_cart(customer, None, 3, is_installment=True)
        cart_item.refresh_from_db()
        assert cart_item.opening_quantity == 10
        assert cart_item.quantity_added == 3
        assert cart_item.closing_quantity == 13
        assert cart_item.is_installment
        assert not cart_item.order_now

        catalog_item.add_to_cart(customer, None, 4, is_installment=True, order_now=True)
        cart_item.refresh_from_db()
        assert cart_item.opening_quantity == 13
        assert cart_item.quantity_added == 4
        assert cart_item.closing_quantity == 17
        assert cart_item.is_installment
        assert cart_item.order_now


from tests.restrictions_mgt.test_models import TestEnterPriseSetupRules
class TesTReferenceCatalog(TestEnterPriseSetupRules):
    """."""

    MK_ROOT = 'elites_franchise_portal.encounters'
    @mock.patch(MK_ROOT+'.tasks.process_customer_encounter.delay')
    def test_create_reference_catalog(self, mock_process_customer_encounter):
        franchise = Enterprise.objects.filter().first()
        if not franchise:
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
        s_units = baker.make(Units, units_name='packet', enterprise=enterprise_code)
        baker.make(UnitsItemType, item_type=item_type, units=s_units, enterprise=enterprise_code)
        s_units.item_types.set([item_type])
        s_units.save()
        p_units = baker.make(Units, units_name='Dozen', enterprise=enterprise_code)
        baker.make(UnitsItemType, item_type=item_type, units=p_units, enterprise=enterprise_code)
        p_units.item_types.set([item_type])
        p_units.save()
        baker.make(
            ItemUnits, item=item, sales_units=s_units, purchases_units=p_units,
            quantity_of_sale_units_per_purchase_unit=12, enterprise=enterprise_code)
        inventory_item = baker.make(InventoryItem, item=item, enterprise=enterprise_code)
        baker.make(
            InventoryInventoryItem, inventory=self.master_inventory, inventory_item=inventory_item,
            enterprise=enterprise_code)
        baker.make(
            InventoryInventoryItem, inventory=self.default_inventory, inventory_item=inventory_item,
            enterprise=enterprise_code)
        catalog_item = baker.make(
            CatalogItem, inventory_item=inventory_item, enterprise=enterprise_code)
        baker.make(
            CatalogCatalogItem, catalog=self.standard_catalog, catalog_item=catalog_item,
            enterprise=enterprise_code)

        warehouse_item = baker.make(WarehouseItem, item=item, enterprise=enterprise_code)
        warehouse_record1 = baker.make(
            WarehouseRecord, warehouse=self.receiving_warehouse, warehouse_item=warehouse_item,
            record_type='ADD', quantity_recorded=15, unit_price=300, enterprise=enterprise_code)
        assert warehouse_record1
        warehouse_record2 = baker.make(
            WarehouseRecord, warehouse=self.receiving_warehouse, warehouse_item=warehouse_item,
            record_type='REMOVE', removal_type='INVENTORY', quantity_recorded=10,
            unit_price=300, enterprise=enterprise_code)
        assert warehouse_record2
        # assert self.master_inventory.summary[0]['quantity'] == 10
        # assert self.default_inventory.summary[0]['quantity'] == 10
        inventory_record1 = baker.make(
            InventoryRecord, inventory=self.default_inventory, inventory_item=inventory_item,
            record_type='REMOVE', removal_type='SALES', quantity_recorded=4, unit_price=320,
            enterprise=enterprise_code)
        assert inventory_record1

        # assert self.master_inventory.summary[0]['quantity'] == 6
        # assert self.default_inventory.summary[0]['quantity'] == 6
        catalog_item.refresh_from_db()

        inventory_record2 = baker.make(
            InventoryRecord, inventory=self.default_inventory, inventory_item=inventory_item,
            record_type='ADD', quantity_recorded=20, unit_price=300, enterprise=enterprise_code)

        assert inventory_record2
        # assert self.master_inventory.summary[0]['quantity'] == 26
        # assert self.default_inventory.summary[0]['quantity'] == 26

        inventory_record3 = baker.make(
            InventoryRecord, inventory=self.default_inventory, inventory_item=inventory_item,
            record_type='REMOVE', removal_type='SALES', quantity_recorded=14, unit_price=320,
            enterprise=enterprise_code)
        assert inventory_record3
        # assert self.master_inventory.summary[0]['quantity'] == 12
        # assert self.default_inventory.summary[0]['quantity'] == 12

        purchase = baker.make(
            Purchase, item=item, quantity_purchased=30, total_price=31000,
            recommended_retail_price=330, quantity_to_inventory=25,
            quantity_to_inventory_on_display=10, enterprise=enterprise_code)

        assert purchase
        # assert self.master_inventory.summary[0]['quantity'] == 25+12 == 37
        # assert self.default_inventory.summary[0]['quantity'] == 25+12 == 37
        # assert reference_catalog.available_quantity == 25+12 == 37

        customer = baker.make(
            Customer, customer_number=9876, first_name='John',
            last_name='Wick', other_names='Baba Yaga', account_number='712345678',
            phone_no='+254712345678', email='johnwick@parabellum.com')
        billing = [
            {
                'catalog_item': str(catalog_item.id),
                'item_name': catalog_item.inventory_item.item.item_name,
                'quantity': 5,
                'unit_price': 330,
                'total': 1650,
                'sale_type': 'INSTANT'                                  # Instant item
            },
        ]
        payments = [{'means': 'CASH', 'amount': 5000, }]

        encounter = baker.make(
            Encounter, customer=customer, billing=billing, payments=payments,
            enterprise=enterprise_code)

        assert encounter
        # assert self.master_inventory.summary[0]['quantity'] == 37
        # assert self.default_inventory.summary[0]['quantity'] == 37
        catalog_item.refresh_from_db()
        # reference_catalog.refresh_from_db()
        # assert reference_catalog.updated_on > catalog_item.updated_on
        # assert reference_catalog.available_quantity == 37-5 == 32
        import pdb
        pdb.set_trace()

        process_customer_encounter(encounter.id)
        catalog_item.refresh_from_db()
        # reference_catalog.refresh_from_db()
        # assert reference_catalog.available_quantity == 32
        import pdb
        pdb.set_trace()

        billing = [
            {
                'catalog_item': str(catalog_item.id),
                'item_name': catalog_item.inventory_item.item.item_name,
                'quantity': 5,
                'unit_price': 330,
                'total': 1650,
                'sale_type': 'INSTALLMENT'                                  # Installment item
            },
        ]
        payments = [{'means': 'CASH', 'amount': 5000, }]

        encounter = baker.make(
            Encounter, customer=customer, billing=billing, payments=payments,
            enterprise=enterprise_code)
        # assert reference_catalog.available_quantity == 32
        import pdb
        pdb.set_trace()
        assert Order.objects.count() == 1
        order1 = Order.objects.first()
        assert order1.is_cleared == True
        # assert reference_catalog.available_quantity == 32
        import pdb
        pdb.set_trace()

        cart = baker.make(
            Cart, cart_code='EAS-C-10001', customer=customer, enterprise=enterprise_code)
        cart_item = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item, quantity_added=9,
            enterprise=enterprise_code)
        assert cart
        assert cart_item
        # assert reference_catalog.available_quantity == 32
        import pdb
        pdb.set_trace()

        cart.checkout_cart()
        # assert reference_catalog.available_quantity == 32
        import pdb
        pdb.set_trace()
        assert Order.objects.count() == 2
        assert OrderTransaction.objects.count() == 1
        order2 = Order.objects.filter().exclude(id=order1.id).first()
        transaction = baker.make(
            Transaction, transaction_code='#8765', transaction_type='DEPOSIT',
            customer=customer, account_number=customer.account_number, amount=2000,
            transaction_means="CASH", enterprise=enterprise_code)

        assert transaction
        assert OrderTransaction.objects.count() == 2

        # assert reference_catalog.available_quantity == 32-9 == 23
        import pdb
        pdb.set_trace()

        cart = baker.make(
            Cart, cart_code='EAS-C-10002', customer=customer, enterprise=enterprise_code)
        cart_item = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item, quantity_added=7,
            enterprise=enterprise_code)

        order3 = baker.make(Order, customer=customer, enterprise=enterprise_code)
        instant_order_item = baker.make(
            InstantOrderItem, order=order3, enterprise=enterprise_code,
            cart_item=cart_item, confirmation_status='CONFIRMED', amount_paid=2100)
        assert instant_order_item
        # assert reference_catalog.available_quantity == 23
        import pdb
        pdb.set_trace()
        order3.process_order()
        # assert reference_catalog.available_quantity == 23
        import pdb
        pdb.set_trace()
        transaction = baker.make(
            Transaction, transaction_code='#8765', transaction_type='DEPOSIT',
            customer=customer, account_number=customer.account_number, amount=2100,
            transaction_means="CASH", enterprise=enterprise_code)
        # assert reference_catalog.available_quantity == 23 - 7 == 16
        import pdb
        pdb.set_trace()

        # TODO Create Sale
        # assert available quantity, quantity_on_installment_plan
