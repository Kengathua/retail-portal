"""."""

import uuid

import pytest
from django.test import TestCase
from django.core.exceptions import ValidationError

from elites_retail_portal.catalog.models import (
    Section, Catalog, CatalogItem, CatalogCatalogItem, CatalogItemAuditLog)
from elites_retail_portal.customers.models import Customer
from elites_retail_portal.debit.models import (
    InventoryItem, Inventory, InventoryRecord, InventoryInventoryItem)
from elites_retail_portal.enterprises.models import Enterprise
from elites_retail_portal.enterprise_mgt.models import (
    EnterpriseSetupRule, EnterpriseSetupRuleCatalog,
    EnterpriseSetupRuleInventory, EnterpriseSetupRuleWarehouse)
from elites_retail_portal.items.models import (
    Brand, BrandItemType, Category, Item, ItemAttribute, ItemModel, ItemType,
    ItemUnits, UnitsItemType, Units)
from elites_retail_portal.orders.models import (
    Cart, CartItem)
from elites_retail_portal.warehouses.models import Warehouse
from django.contrib.auth import get_user_model

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
        assert str(sec)
        assert sec.section_code == 'FNO-MB/S-SA/2301'
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
        assert str(catalog)
        assert Catalog.objects.count() == 1


class TestCatalogItem(TestCase):
    """."""

    def setUp(self) -> None:
        """."""
        self.franchise = baker.make(Enterprise, name='Elites Age Supermarket')
        enterprise_code = self.franchise.enterprise_code
        self.inventory = baker.make(
            Inventory, inventory_name='Elites Age Supermarket Available Inventory',
            is_default=True, is_master=True,
            is_active=True, inventory_type='AVAILABLE', enterprise=enterprise_code)
        self.catalog = baker.make(
            Catalog, catalog_name='Elites Age Supermarket Standard Catalog',
            is_default=True,
            description='Standard Catalog', is_standard=True, enterprise=enterprise_code)
        warehouse = baker.make(
            Warehouse, warehouse_name='Elites Private Warehouse', is_default=True,
            is_receiving=True,
            enterprise=enterprise_code)
        rule = baker.make(
            EnterpriseSetupRule, name='Elites Age', is_active=True, enterprise=enterprise_code)
        baker.make(
            EnterpriseSetupRuleInventory, rule=rule, inventory=self.inventory,
            enterprise=enterprise_code)
        baker.make(
            EnterpriseSetupRuleWarehouse, rule=rule, warehouse=warehouse,
            enterprise=enterprise_code)
        baker.make(
            EnterpriseSetupRuleCatalog, rule=rule, catalog=self.catalog,
            enterprise=enterprise_code)
        return super().setUp()

    def test_create_catalog_item(self):
        """."""
        enterprise_code = self.franchise.enterprise_code
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
        item_units = baker.make(
            ItemUnits, item=item, sales_units=s_units, purchases_units=p_units,
            quantity_of_sale_units_per_purchase_unit=12, enterprise=enterprise_code)
        baker.make(
            ItemAttribute, item=item, attribute_type='SPECIAL OFFER',
            attribute_value='Special Offer One', enterprise=enterprise_code)
        baker.make(
            ItemAttribute, item=item, attribute_type='SPECIAL FEATURE',
            attribute_value='Special Feature One', enterprise=enterprise_code)
        baker.make(
            ItemAttribute, item=item, attribute_type='SPECIFICATION',
            attribute_value='Specification One', enterprise=enterprise_code)
        baker.make(
            ItemAttribute, item=item, attribute_type='DESCRIPTION',
            attribute_value='Description', enterprise=enterprise_code)

        inventory_item = baker.make(InventoryItem, item=item, enterprise=enterprise_code)
        baker.make(
            InventoryInventoryItem, inventory=self.inventory, inventory_item=inventory_item)
        catalog_item_recipe = Recipe(
            CatalogItem, inventory_item=inventory_item, enterprise=enterprise_code)

        item_units.is_active = False
        item_units.save()

        with pytest.raises(ValidationError) as ve:
            catalog_item_recipe.make()
        msg = 'The SAMSUNG GE731K-B SUT COOKER does not have active units'
        assert msg in ve.value.messages

        item_units.is_active = True
        item_units.save()

        catalog_item = catalog_item_recipe.make()

        assert str(catalog_item)
        assert catalog_item.item_heading == 'SAMSUNG GE731K-B SUT Special Feature One COOKER, packet Special Offer One'
        assert CatalogItem.objects.count() == 1

    def test_fail_create_catalog_item_exists(self):
        """."""
        enterprise_code = self.franchise.enterprise_code
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
            InventoryInventoryItem, inventory=self.inventory, inventory_item=inventory_item)
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
        enterprise_code = self.franchise.enterprise_code
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
            InventoryInventoryItem, inventory=self.inventory, inventory_item=inventory_item)
        catalog_item = baker.make(
            CatalogItem, inventory_item=inventory_item, marked_price=300,
            threshold_price=200, enterprise=enterprise_code)
        customer = baker.make(
            Customer, customer_number=9876, first_name='John', last_name='Wick',
            phone_no='+254712345678', email='johnwick@parabellum.com')

        catalog_item.add_to_cart(customer)
        assert Cart.objects.count() == 1
        assert CartItem.objects.count() == 1
        cart_item = CartItem.objects.first()
        cart_item.selling_price == 300

        with pytest.raises(ValidationError) as ve:
            catalog_item.add_to_cart(customer, price=100)
        msg = 'The selling price KSH 100 is below the threshold price KSH 200 by KSH 100.0'
        assert msg in ve.value.messages
            
        catalog_item.add_to_cart(customer, price=200)
        cart_item.refresh_from_db()
        assert cart_item.selling_price == 200

        enterprise_user = get_user_model().objects.create_superuser(
                email='user@email.com', first_name='Test', last_name='User',
                guid=uuid.uuid4(),
                password='Testpass254$', enterprise=enterprise_code)
        customer.enterprise_user = enterprise_user
        customer.save()
        catalog_item.updated_by = enterprise_user.id
        catalog_item.save()
        catalog_item.add_to_cart(customer=None, price=200)
        cart_item.refresh_from_db()
        cart_item.cart.customer == customer

    def test_add_item_to_cart_specify_quantity(self):
        """."""
        enterprise_code = self.franchise.enterprise_code
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
            InventoryInventoryItem, inventory=self.inventory, inventory_item=inventory_item)
        catalog_item = baker.make(
            CatalogItem, inventory_item=inventory_item, enterprise=enterprise_code)
        customer = baker.make(
            Customer, customer_number=9876, first_name='John', last_name='Wick',
            phone_no='+254712345678', email='johnwick@parabellum.com')
        catalog_item.add_to_cart(customer, quantity=2)
        assert Cart.objects.count() == 1
        assert CartItem.objects.count() == 1

        cart_item = CartItem.objects.get(
            catalog_item__inventory_item=inventory_item)
        cart_item.opening_quantity == 0
        cart_item.quantity_added == 2
        cart_item.closing_quantity == 2

    def test_add_item_to_cart_multiple_times(self):
        """."""
        enterprise_code = self.franchise.enterprise_code
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
            InventoryInventoryItem, inventory=self.inventory, inventory_item=inventory_item)
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

    def test_get_quantity(self):
        """."""
        enterprise_code = self.franchise.enterprise_code
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

        self.inventory.is_master = False
        self.inventory.save()
        inventory_item = baker.make(InventoryItem, item=item, enterprise=enterprise_code)
        baker.make(
            InventoryInventoryItem, inventory=self.inventory, inventory_item=inventory_item)
        catalog_item_recipe = Recipe(
            CatalogItem, inventory_item=inventory_item, enterprise=enterprise_code)
        with pytest.raises(ValidationError) as ve:
            catalog_item_recipe.make()
        msg = 'Your enterprise does not have a master Inventory. Please set up one first'
        assert msg in ve.value.messages

        self.inventory.is_master = True
        self.inventory.save()
        catalog_item = catalog_item_recipe.make()
        assert catalog_item.quantity == 0
        assert catalog_item.marked_price == 0
        assert catalog_item.discount_amount == 0
        assert catalog_item.selling_price == 0
        assert catalog_item.threshold_price == 0

        baker.make(
            InventoryRecord, inventory=self.inventory, inventory_item=inventory_item,
            record_type='ADD', quantity_recorded=15, unit_price=300, enterprise=enterprise_code)

        catalog_item.refresh_from_db()
        assert catalog_item.quantity == 15
        assert catalog_item.marked_price == 300
        assert catalog_item.discount_amount == 0
        assert catalog_item.selling_price == 300
        assert catalog_item.threshold_price == 300

    def test_add_to_catalogs(self):
        enterprise_code = self.franchise.enterprise_code
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
        inventory_item = baker.make(InventoryItem, item=item, enterprise=enterprise_code)
        baker.make(
            InventoryInventoryItem, inventory=self.inventory, inventory_item=inventory_item)
        catalog_item = baker.make(
            CatalogItem, inventory_item=inventory_item, enterprise=enterprise_code)
        user = get_user_model().objects.create_superuser(
                email='user@email.com', first_name='Test', last_name='User',
                guid=uuid.uuid4(),
                password='Testpass254$', enterprise=enterprise_code)

        with pytest.raises(ValidationError) as ve:
            catalog_item.add_to_catalogs(user, [])
        msg = 'Please select the catalogs you want to add the item to'
        assert msg in ve.value.messages

        catalog_item.add_to_catalogs(user, [self.catalog])
        assert CatalogCatalogItem.objects.count() == 1

class TestCatalogCatalogItem(TestCase):
    """Catalog catalog item tests."""

    def test_create_catalog_catalog_item(self):
        """."""
        franchise = baker.make(Enterprise, name='Elites Age Supermarket')
        enterprise_code = franchise.enterprise_code
        inventory = baker.make(
            Inventory, inventory_name='Elites Age Supermarket Available Inventory',
            is_default=True, is_master=True,
            is_active=True, inventory_type='AVAILABLE', enterprise=enterprise_code)
        catalog = baker.make(
            Catalog, catalog_name='Elites Age Supermarket Standard Catalog',
            is_default=True,
            description='Standard Catalog', is_standard=True, enterprise=enterprise_code)
        warehouse = baker.make(
            Warehouse, warehouse_name='Elites Private Warehouse', is_default=True,
            is_receiving=True,
            enterprise=enterprise_code)
        rule = baker.make(
            EnterpriseSetupRule, name='Elites Age', is_active=True, enterprise=enterprise_code)
        baker.make(
            EnterpriseSetupRuleInventory, rule=rule, inventory=inventory,
            enterprise=enterprise_code)
        baker.make(
            EnterpriseSetupRuleWarehouse, rule=rule, warehouse=warehouse,
            enterprise=enterprise_code)
        baker.make(
            EnterpriseSetupRuleCatalog, rule=rule, catalog=catalog,
            enterprise=enterprise_code)
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
            InventoryInventoryItem, inventory=inventory, inventory_item=inventory_item)
        catalog_item = baker.make(
            CatalogItem, inventory_item=inventory_item, enterprise=enterprise_code)
        catalog_catalog_item = baker.make(
            CatalogCatalogItem, catalog=catalog, catalog_item=catalog_item, enterprise=enterprise_code)

        assert catalog_catalog_item
        assert CatalogCatalogItem.objects.count() == 1

        assert catalog_item.catalogs_names == 'Elites Age Supermarket Standard Catalog'


class TestCatalogItemAuditLog(TestCase):
    """."""

    def test_create_catalog_item_audit_log(self):
        """."""
        franchise = baker.make(Enterprise, name='Elites Age Supermarket')
        enterprise_code = franchise.enterprise_code
        inventory = baker.make(
            Inventory, inventory_name='Elites Age Supermarket Available Inventory',
            is_default=True, is_master=True,
            is_active=True, inventory_type='AVAILABLE', enterprise=enterprise_code)
        catalog = baker.make(
            Catalog, catalog_name='Elites Age Supermarket Standard Catalog',
            is_default=True,
            description='Standard Catalog', is_standard=True, enterprise=enterprise_code)
        warehouse = baker.make(
            Warehouse, warehouse_name='Elites Private Warehouse', is_default=True,
            is_receiving=True,
            enterprise=enterprise_code)
        rule = baker.make(
            EnterpriseSetupRule, name='Elites Age', is_active=True, enterprise=enterprise_code)
        baker.make(
            EnterpriseSetupRuleInventory, rule=rule, inventory=inventory,
            enterprise=enterprise_code)
        baker.make(
            EnterpriseSetupRuleWarehouse, rule=rule, warehouse=warehouse,
            enterprise=enterprise_code)
        baker.make(
            EnterpriseSetupRuleCatalog, rule=rule, catalog=catalog,
            enterprise=enterprise_code)
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
            InventoryInventoryItem, inventory=inventory, inventory_item=inventory_item)
        catalog_item = baker.make(
            CatalogItem, inventory_item=inventory_item, enterprise=enterprise_code)
        assert CatalogItemAuditLog.objects.count() == 1
        log1 =  CatalogItemAuditLog.objects.first()

        log1.quantity_before = 0
        log1.quantity_recorded = 10
        log1.quantity_after = 12

        with pytest.raises(ValidationError) as ve:
            log1.save()
        msg = 'The closing quantity is 12.0 is not equal to the expected closing quantity 10.0'
        assert msg in ve.value.messages

        audit_recipe = Recipe(
            CatalogItemAuditLog, catalog_item=catalog_item, audit_source='INVENTORY RECORD',
            enterprise=enterprise_code)
        with pytest.raises(ValidationError) as ve:
            audit_recipe.make()
        msg = 'An audit coming from inventory records should have the inventory record attached to it'
        assert msg in ve.value.messages
