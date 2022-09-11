import pytest
from django.test import TestCase
from django.core.exceptions import ValidationError

from elites_franchise_portal.enterprises.models import Enterprise
from elites_franchise_portal.items.models import (
    Brand, BrandItemType, Category, Item, ItemModel, ItemType,
    ItemUnits, UnitsItemType, Units)
from elites_franchise_portal.debit.models import (
    InventoryItem, Inventory, InventoryInventoryItem, Sale, SaleRecord)
from elites_franchise_portal.catalog.models import (
    Section, Catalog, CatalogItem, CatalogCatalogItem, ReferenceCatalog)
from elites_franchise_portal.orders.models import Cart, CartItem
from elites_franchise_portal.customers.models import Customer

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

    def test_create_reference_catalog(self):
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
        reference_catalog = baker.make(
            ReferenceCatalog, catalog_item=catalog_item, quantity=10, quantity_on_installment_plan=5,
            enterprise=enterprise_code)
        assert not reference_catalog.available_quantity

        # TODO Create Inventory Record - ADD
        # assert available quantity, quantity_on_installment_plan
        # TODO Create Inventory Record - REMOVE
        # assert available quantity, quantity_on_installment_plan
        # TODO Create Purchase Record - REMOVE
        # assert available quantity, quantity_on_installment_plan
        # TODO Create New Encounter Record - REMOVE
        # assert available quantity, quantity_on_installment_plan
        # TODO Create Cart
        # assert available quantity, quantity_on_installment_plan
        # TODO Create Order
        # assert available quantity, quantity_on_installment_plan
        # TODO Create Sale
        # assert available quantity, quantity_on_installment_plan
        