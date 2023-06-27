"""Sales tests file."""
import uuid

from django.test import TestCase
from django.contrib.auth import get_user_model
from elites_retail_portal.customers.models import Customer
from elites_retail_portal.debit.models.inventory import InventoryInventoryItem
from elites_retail_portal.enterprise_mgt.models import (
    EnterpriseSetupRule, EnterpriseSetupRuleInventory,
    EnterpriseSetupRuleCatalog, EnterpriseSetupRuleWarehouse)
from elites_retail_portal.catalog.models import Catalog
from elites_retail_portal.warehouses.models import Warehouse
from elites_retail_portal.items.models import (
    Brand, BrandItemType, Category, Item, ItemModel, ItemType,
    ItemUnits, UnitsItemType, Units)
from elites_retail_portal.debit.models import (
    Inventory, InventoryItem, InventoryRecord, Sale, SaleItem)
from elites_retail_portal.catalog.models import CatalogItem
from elites_retail_portal.enterprises.models import Enterprise
from elites_retail_portal.customers.models import Customer
from elites_retail_portal.orders.models import Order

from model_bakery import baker


class TestSale(TestCase):
    """."""

    def test_create_sale(self):
        """."""
        franchise = baker.make(Enterprise, name='Elites Age Supermarket')
        enterprise_code = franchise.enterprise_code
        test_user = get_user_model().objects.create_superuser(
            email='testuser@email.com', first_name='Test', last_name='User',
            guid=uuid.uuid4(), password='Testpass254$', enterprise=enterprise_code)
        customer = baker.make(
            Customer, customer_number=9876, first_name='John', last_name='Wick',
            is_site=True, enterprise_user=test_user, phone_no='+254712345678',
            email='johnwick@parabellum.com', enterprise=enterprise_code)
        sale = baker.make(Sale, customer=customer, enterprise=enterprise_code)

        assert sale
        assert Sale.objects.count() == 1

    def test_create_sale_default_franchise_customer(self):
        """."""
        franchise = baker.make(Enterprise, name='Elites Age Supermarket')
        enterprise_code = franchise.enterprise_code
        test_user = get_user_model().objects.create_superuser(
            email='testuser@email.com', first_name='Test', last_name='User',
            guid=uuid.uuid4(), password='Testpass254$', enterprise=enterprise_code)
        customer = baker.make(
            Customer, customer_number=9876, first_name='John', last_name='Wick',
            is_site=True, enterprise_user=test_user, phone_no='+254712345678',
            email='johnwick@parabellum.com', enterprise=enterprise_code)
        sale = baker.make(
            Sale, enterprise=enterprise_code, created_by=test_user.id, updated_by=test_user.id)

        sale.refresh_from_db()
        assert sale
        assert Sale.objects.count() == 1
        assert sale.customer == customer


class TestSaleItem(TestCase):
    """."""

    def test_create_sale_record(self):
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
        item_model1 = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731K-B/SUT',
            enterprise=enterprise_code)
        item_model2 = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731L-C/SUT',
            enterprise=enterprise_code)
        item_model3 = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731M-D/SUT',
            enterprise=enterprise_code)
        item_model4 = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731N-E/SUT',
            enterprise=enterprise_code)
        item1 = baker.make(
            Item, item_model=item_model1, barcode='838383885673', make_year=2020,
            enterprise=enterprise_code)
        item2 = baker.make(
            Item, item_model=item_model2, barcode='838380987383', make_year=2020,
            enterprise=enterprise_code)
        item3 = baker.make(
            Item, item_model=item_model3, barcode='678838383883', make_year=2020,
            enterprise=enterprise_code)
        item4 = baker.make(
            Item, item_model=item_model4, barcode='838383887654', make_year=2020,
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
        baker.make(
            ItemUnits, item=item3, sales_units=s_units, purchases_units=p_units,
            quantity_of_sale_units_per_purchase_unit=12, enterprise=enterprise_code)
        baker.make(
            ItemUnits, item=item4, sales_units=s_units, purchases_units=p_units,
            quantity_of_sale_units_per_purchase_unit=12, enterprise=enterprise_code)
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
            is_receiving=True, enterprise=enterprise_code)
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
        inventory_item1 = baker.make(
            InventoryItem, item=item1, enterprise=enterprise_code)
        inventory_item2 = baker.make(
            InventoryItem, item=item2, enterprise=enterprise_code)
        inventory_item3 = baker.make(
            InventoryItem, item=item3, enterprise=enterprise_code)
        inventory_item4 = baker.make(
            InventoryItem, item=item4, enterprise=enterprise_code)

        baker.make(
            InventoryInventoryItem, inventory=inventory,
            inventory_item=inventory_item1, enterprise=enterprise_code)
        baker.make(
            InventoryInventoryItem, inventory=inventory,
            inventory_item=inventory_item2, enterprise=enterprise_code)
        baker.make(
            InventoryInventoryItem, inventory=inventory,
            inventory_item=inventory_item3, enterprise=enterprise_code)
        baker.make(
            InventoryInventoryItem, inventory=inventory,
            inventory_item=inventory_item4, enterprise=enterprise_code)

        baker.make(
            InventoryRecord, inventory=inventory, inventory_item=inventory_item1,
            record_type='ADD', quantity_recorded=20, unit_price=350,
            enterprise=enterprise_code)
        baker.make(
            InventoryRecord, inventory=inventory, inventory_item=inventory_item2,
            record_type='ADD', quantity_recorded=10, unit_price=1000,
            enterprise=enterprise_code)
        baker.make(
            InventoryRecord, inventory=inventory, inventory_item=inventory_item3,
            record_type='ADD', quantity_recorded=5, unit_price=2750,
            enterprise=enterprise_code)
        baker.make(
            InventoryRecord, inventory=inventory, inventory_item=inventory_item4,
            record_type='ADD', quantity_recorded=5, unit_price=2750,
            enterprise=enterprise_code)
        catalog_item1 = baker.make(
            CatalogItem, inventory_item=inventory_item1, enterprise=enterprise_code)
        catalog_item2 = baker.make(
            CatalogItem, inventory_item=inventory_item2, enterprise=enterprise_code)
        catalog_item3 = baker.make(
            CatalogItem, inventory_item=inventory_item3, enterprise=enterprise_code)
        catalog_item4 = baker.make(
            CatalogItem, inventory_item=inventory_item4, enterprise=enterprise_code)
        customer = baker.make(
            Customer, customer_number=9876, first_name='John', last_name='Wick',
            phone_no='+254712345678', email='johnwick@parabellum.com')

        order = baker.make(Order, order_number='#87654', enterprise=enterprise_code)
        sale = baker.make(Sale, customer=customer, order=order, enterprise=enterprise_code)
        baker.make(
            SaleItem, sale=sale, quantity_sold=1, selling_price=560,
            catalog_item=catalog_item1, enterprise=enterprise_code)
        baker.make(
            SaleItem, sale=sale, quantity_sold=2, selling_price=340,
            catalog_item=catalog_item2, enterprise=enterprise_code)
        baker.make(
            SaleItem, sale=sale, quantity_sold=3, selling_price=230,
            catalog_item=catalog_item3, enterprise=enterprise_code)
        baker.make(
            SaleItem, sale=sale, quantity_sold=4, selling_price=100,
            catalog_item=catalog_item4, enterprise=enterprise_code)

        assert SaleItem.objects.count() == 4
