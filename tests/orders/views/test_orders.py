"""Tests for order views file."""

import json
import datetime
from django.urls import reverse
from rest_framework.test import APITestCase

from elites_retail_portal.enterprise_mgt.models import (
    EnterpriseSetupRule, EnterpriseSetupRuleInventory,
    EnterpriseSetupRuleCatalog, EnterpriseSetupRuleWarehouse)
from elites_retail_portal.items.models import (
    Brand, BrandItemType, Category, Item, ItemModel, ItemType,
    ItemUnits, UnitsItemType, Units)
from elites_retail_portal.debit.models import (
    InventoryItem, InventoryRecord, Inventory, InventoryInventoryItem)
from elites_retail_portal.enterprises.models import Enterprise
from elites_retail_portal.enterprises.models import Enterprise
from elites_retail_portal.catalog.models import (
    CatalogItem, Catalog, CatalogCatalogItem)
from elites_retail_portal.orders.models import (
    Cart, CartItem, Order, InstantOrderItem,
    InstallmentsOrderItem, Installment, OrderTransaction)
from elites_retail_portal.customers.models import Customer
from elites_retail_portal.warehouses.models import Warehouse
from elites_retail_portal.transactions.models import Transaction, Payment

from tests.utils import APITests

from model_bakery import baker
from model_bakery.recipe import Recipe
from tests.utils.login_mixins import authenticate_test_user


class TestOrderView(APITests, APITestCase):
    """."""

    def setUp(self):
        """."""
        franchise = baker.make(
            Enterprise, reg_no='BS-9049444', name='Enterprise One',
            enterprise_code='EAL-E/EO-MB/2301-01', business_type='SHOP')
        enterprise_code = franchise.enterprise_code
        customer = baker.make(
            Customer, customer_number=9876, first_name='John',
            last_name='Wick', other_names='Baba Yaga',
            phone_no='+254712345678', email='johnwick@parabellum.com', enterprise=enterprise_code)
        cart = baker.make(
            Cart, cart_code='EAS-C-10001', customer=customer, enterprise=enterprise_code)
        self.recipe = Recipe(
            Order, customer=customer, cart_code=cart.cart_code, enterprise=enterprise_code)

    url = 'v1:orders:order'

    def test_delete(self, status_code=204):
        pass

    def test_update_order_items(self, status_code=201):
        order = self.make()
        self.client = authenticate_test_user()
        enterprise_code = order.enterprise
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
            ItemModel, brand=brand, item_type=item_type, model_name='AE731K-B/SUT',
            enterprise=enterprise_code)
        item_model2 = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='BE864L-C/SUT',
            enterprise=enterprise_code)
        item_model3 = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='CE875M-D/SUT',
            enterprise=enterprise_code)
        item_model4 = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='DE256N-E/SUT',
            enterprise=enterprise_code)
        item_model5 = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='EY864N-E/SUT',
            enterprise=enterprise_code)
        item_model6 = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='FP239N-E/SUT',
            enterprise=enterprise_code)
        item_model7 = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE6491N-E/SUT',
            enterprise=enterprise_code)
        item_model8 = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='HLR746P-E/SUT',
            enterprise=enterprise_code)

        item1 = baker.make(
            Item, item_model=item_model1, barcode='8765655673', make_year=2020,
            enterprise=enterprise_code)
        item2 = baker.make(
            Item, item_model=item_model2, barcode='23456898765', make_year=2020,
            enterprise=enterprise_code)
        item3 = baker.make(
            Item, item_model=item_model3, barcode='4567876432', make_year=2020,
            enterprise=enterprise_code)
        item4 = baker.make(
            Item, item_model=item_model4, barcode='56765434567', make_year=2020,
            enterprise=enterprise_code)
        item5 = baker.make(
            Item, item_model=item_model5, barcode='838383885673', make_year=2020,
            enterprise=enterprise_code)
        item6 = baker.make(
            Item, item_model=item_model6, barcode='838380987383', make_year=2020,
            enterprise=enterprise_code)
        item7 = baker.make(
            Item, item_model=item_model7, barcode='678838383883', make_year=2020,
            enterprise=enterprise_code)
        item8 = baker.make(
            Item, item_model=item_model8, barcode='838383887654', make_year=2020,
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
        baker.make(
            ItemUnits, item=item5, sales_units=s_units, purchases_units=p_units,
            quantity_of_sale_units_per_purchase_unit=12, enterprise=enterprise_code)
        baker.make(
            ItemUnits, item=item6, sales_units=s_units, purchases_units=p_units,
            quantity_of_sale_units_per_purchase_unit=12, enterprise=enterprise_code)
        baker.make(
            ItemUnits, item=item7, sales_units=s_units, purchases_units=p_units,
            quantity_of_sale_units_per_purchase_unit=12, enterprise=enterprise_code)
        baker.make(
            ItemUnits, item=item8, sales_units=s_units, purchases_units=p_units,
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

        inventory_item1 = baker.make(InventoryItem, item=item1, enterprise=enterprise_code)
        inventory_item2 = baker.make(InventoryItem, item=item2, enterprise=enterprise_code)
        inventory_item3 = baker.make(InventoryItem, item=item3, enterprise=enterprise_code)
        inventory_item4 = baker.make(InventoryItem, item=item4, enterprise=enterprise_code)
        inventory_item5 = baker.make(InventoryItem, item=item5, enterprise=enterprise_code)
        inventory_item6 = baker.make(InventoryItem, item=item6, enterprise=enterprise_code)
        inventory_item7 = baker.make(InventoryItem, item=item7, enterprise=enterprise_code)
        inventory_item8 = baker.make(InventoryItem, item=item8, enterprise=enterprise_code)

        baker.make(
            InventoryInventoryItem, inventory=inventory, inventory_item=inventory_item1,
            enterprise=enterprise_code)
        baker.make(
            InventoryInventoryItem, inventory=inventory, inventory_item=inventory_item2,
            enterprise=enterprise_code)
        baker.make(
            InventoryInventoryItem, inventory=inventory, inventory_item=inventory_item3,
            enterprise=enterprise_code)
        baker.make(
            InventoryInventoryItem, inventory=inventory, inventory_item=inventory_item4,
            enterprise=enterprise_code)
        baker.make(
            InventoryInventoryItem, inventory=inventory, inventory_item=inventory_item5,
            enterprise=enterprise_code)
        baker.make(
            InventoryInventoryItem, inventory=inventory, inventory_item=inventory_item6,
            enterprise=enterprise_code)
        baker.make(
            InventoryInventoryItem, inventory=inventory, inventory_item=inventory_item7,
            enterprise=enterprise_code)
        baker.make(
            InventoryInventoryItem, inventory=inventory, inventory_item=inventory_item8,
            enterprise=enterprise_code)

        baker.make(
            InventoryRecord, inventory=inventory, inventory_item=inventory_item1,
            record_type='ADD', quantity_recorded=20, unit_price=350, enterprise=enterprise_code)
        baker.make(
            InventoryRecord, inventory=inventory, inventory_item=inventory_item2,
            record_type='ADD', quantity_recorded=10, unit_price=1000, enterprise=enterprise_code)
        baker.make(
            InventoryRecord, inventory=inventory, inventory_item=inventory_item3,
            record_type='ADD', quantity_recorded=5, unit_price=2750, enterprise=enterprise_code)
        baker.make(
            InventoryRecord, inventory=inventory, inventory_item=inventory_item4,
            record_type='ADD', quantity_recorded=15, unit_price=500, enterprise=enterprise_code)
        baker.make(
            InventoryRecord, inventory=inventory, inventory_item=inventory_item5,
            record_type='ADD', quantity_recorded=23, unit_price=1200, enterprise=enterprise_code)
        baker.make(
            InventoryRecord, inventory=inventory, inventory_item=inventory_item6,
            record_type='ADD', quantity_recorded=65, unit_price=250, enterprise=enterprise_code)
        baker.make(
            InventoryRecord, inventory=inventory, inventory_item=inventory_item7,
            record_type='ADD', quantity_recorded=27, unit_price=1350, enterprise=enterprise_code)
        baker.make(
            InventoryRecord, inventory=inventory, inventory_item=inventory_item8,
            record_type='ADD', quantity_recorded=30, unit_price=3000, enterprise=enterprise_code)

        catalog_item1 = baker.make(
            CatalogItem, inventory_item=inventory_item1, enterprise=enterprise_code)
        catalog_item2 = baker.make(
            CatalogItem, inventory_item=inventory_item2, enterprise=enterprise_code)
        catalog_item3 = baker.make(
            CatalogItem, inventory_item=inventory_item3, enterprise=enterprise_code)
        catalog_item4 = baker.make(
            CatalogItem, inventory_item=inventory_item4, enterprise=enterprise_code)
        catalog_item5 = baker.make(
            CatalogItem, inventory_item=inventory_item5, enterprise=enterprise_code)
        catalog_item6 = baker.make(
            CatalogItem, inventory_item=inventory_item6, enterprise=enterprise_code)
        catalog_item7 = baker.make(
            CatalogItem, inventory_item=inventory_item7, enterprise=enterprise_code)
        catalog_item8 = baker.make(
            CatalogItem, inventory_item=inventory_item8, enterprise=enterprise_code)

        baker.make(
            CatalogCatalogItem, catalog=catalog, catalog_item=catalog_item1,
            enterprise=enterprise_code)
        baker.make(
            CatalogCatalogItem, catalog=catalog, catalog_item=catalog_item2,
            enterprise=enterprise_code)
        baker.make(
            CatalogCatalogItem, catalog=catalog, catalog_item=catalog_item3,
            enterprise=enterprise_code)
        baker.make(
            CatalogCatalogItem, catalog=catalog, catalog_item=catalog_item4,
            enterprise=enterprise_code)
        baker.make(
            CatalogCatalogItem, catalog=catalog, catalog_item=catalog_item5,
            enterprise=enterprise_code)
        baker.make(
            CatalogCatalogItem, catalog=catalog, catalog_item=catalog_item6,
            enterprise=enterprise_code)
        baker.make(
            CatalogCatalogItem, catalog=catalog, catalog_item=catalog_item7,
            enterprise=enterprise_code)
        baker.make(
            CatalogCatalogItem, catalog=catalog, catalog_item=catalog_item8,
            enterprise=enterprise_code)

        cart = Cart.objects.get(cart_code=order.cart_code, enterprise=enterprise_code)
        cart_item1 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item1, quantity_added=3,
            enterprise=enterprise_code)
        cart_item2 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item2, quantity_added=1,
            enterprise=enterprise_code)
        cart_item3 = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item3, quantity_added=3,
            enterprise=enterprise_code)
        instant_order_item = baker.make(
            InstantOrderItem, order=order, enterprise=enterprise_code,
            cart_item=cart_item1, confirmation_status='CONFIRMED', amount_paid=350)
        installment_order_item1 = baker.make(
            InstallmentsOrderItem, enterprise=enterprise_code, deposit_amount=200,
            order=order, cart_item=cart_item2, confirmation_status='CONFIRMED')
        installment_order_item2 = baker.make(
            InstallmentsOrderItem, enterprise=enterprise_code, deposit_amount=800,
            order=order, cart_item=cart_item3, confirmation_status='CONFIRMED')

        encounter = {
            "updated_order_items_data": [
                {
                    "order_item": str(instant_order_item.id),
                    "quantity": "3",
                    "order_type": "INSTANT",
                    "status": "CANCELED"
                },
                {
                    "order_item": str(installment_order_item1.id),
                    "quantity": "2",
                    "order_type": "INSTALLMENT",
                    "status": None,
                },
                {
                    "order_item": str(installment_order_item2.id),
                    "quantity": "2",
                    "order_type": "INSTALLMENT",
                    "status": "CANCELED"
                },
            ],
            "new_catalog_items_data": [
                {
                    "catalog_item": str(catalog_item5.id),
                    "quantity": 3,
                    "sale_type": "INSTANT",
                    "unit_price": "1500",
                },
                {
                    "catalog_item": str(catalog_item6.id),
                    "quantity": 5,
                    "sale_type": "INSTANT",
                    "unit_price": "300",
                },
                {
                    "catalog_item": str(catalog_item7.id),
                    "quantity": 2,
                    "sale_type": "INSTALLMENT",
                    "unit_price": "1700",
                },
                {
                    "catalog_item": str(catalog_item8.id),
                    "quantity": 3,
                    "sale_type": "INSTALLMENT",
                    "unit_price": "4000",
                },
            ],
            "additional_payments": [
                {
                    "means": "CASH",
                    "amount": "5000",
                }
            ]
        }
        url = reverse(self.url + '-update-order-items', kwargs={'pk': order.id})
        encounter = json.loads(json.dumps(encounter))
        # resp = self.client.post(url, encounter, format='json')
        # assert resp.status_code == status_code == 201

class TestInstantOrderItemView(APITests, APITestCase):
    """."""

    def setUp(self):
        """."""
        franchise = baker.make(
            Enterprise, reg_no='BS-9049444', name='Enterprise One',
            enterprise_code='EAL-E/EO-MB/2301-01', business_type='SHOP')
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
        p_units = s_units
        baker.make(
            ItemUnits, item=item, sales_units=s_units, purchases_units=p_units,
            quantity_of_sale_units_per_purchase_unit=1, enterprise=enterprise_code)

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

        inventory_item = baker.make(InventoryItem, item=item, enterprise=enterprise_code)
        baker.make(
            InventoryInventoryItem, inventory=inventory, inventory_item=inventory_item)
        baker.make(
            InventoryRecord, inventory=inventory, inventory_item=inventory_item, record_type='ADD',
            quantity_recorded=20, unit_price=350, enterprise=enterprise_code)
        catalog_item = baker.make(
            CatalogItem, inventory_item=inventory_item, enterprise=enterprise_code)
        baker.make(
            CatalogCatalogItem, catalog=catalog, catalog_item=catalog_item,
            enterprise=enterprise_code)
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
        self.recipe = Recipe(
            InstantOrderItem, order=order, enterprise=franchise.enterprise_code,
            cart_item=cart_item, confirmation_status='CONFIRMED', amount_paid=350)

    url = 'v1:orders:instantorderitem'

    def test_post(self, status_code=201):
        pass

    def test_put(self, status_code=200):
        pass

    def test_patch(self, status_code=200):
        pass


class TestInstallmentOrderItemView(APITests, APITestCase):
    """."""

    def setUp(self):
        """."""
        end_date = datetime.datetime.now().date() + datetime.timedelta(90)
        franchise = baker.make(
            Enterprise, reg_no='BS-9049444', name='Enterprise One',
            enterprise_code='EAL-E/EO-MB/2301-01', business_type='SHOP')
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
        p_units = s_units
        baker.make(
            ItemUnits, item=item, sales_units=s_units, purchases_units=p_units,
            quantity_of_sale_units_per_purchase_unit=1, enterprise=enterprise_code)

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

        inventory_item = baker.make(InventoryItem, item=item, enterprise=enterprise_code)
        baker.make(
            InventoryInventoryItem, inventory=inventory, inventory_item=inventory_item,
            enterprise=enterprise_code)
        baker.make(
            InventoryRecord, inventory=inventory, inventory_item=inventory_item,
            record_type='ADD', quantity_recorded=20, unit_price=350, enterprise=enterprise_code)
        catalog_item = baker.make(
            CatalogItem, inventory_item=inventory_item, enterprise=enterprise_code)
        baker.make(
            CatalogCatalogItem, catalog=catalog, catalog_item=catalog_item,
            enterprise=enterprise_code)
        customer = baker.make(
            Customer, title='Mr', customer_number=9876, first_name='John',
            last_name='Wick', other_names='Baba Yaga', gender='MALE',
            phone_no='+254712345678', email='johnwick@parabellum.com')
        cart = baker.make(
            Cart, cart_code='EAS-C-10001', customer=customer, enterprise=enterprise_code)
        cart_item = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item, quantity_added=2,
            enterprise=enterprise_code)
        order = baker.make(Order, customer=customer, enterprise=enterprise_code)
        self.recipe = Recipe(
            InstallmentsOrderItem, enterprise=franchise.enterprise_code,
            order=order, cart_item=cart_item,  confirmation_status='CONFIRMED',
            amount_paid=150, deposit_amount=150, end_date=end_date)

    url = 'v1:orders:installmentorderitem'

    def test_post(self, status_code=201):
        self.client = authenticate_test_user()
        instance = self.make()
        test_data = self.get_test_data(instance)
        url = reverse(self.url + '-list')
        resp = self.client.post(url, test_data)
        assert resp.status_code == status_code, '{}, {}, {}'.format(resp.content, url, test_data)  # noqa
        if resp.status_code != 201:
            return resp

        self.compare_dicts(test_data, resp.data)

        return test_data, resp

    def test_put(self, status_code=200):
        pass

    def test_patch(self, status_code=200):
        pass


class TestInstallmentView(APITests, APITestCase):
    """."""

    def setUp(self):
        """."""
        franchise = baker.make(
            Enterprise, reg_no='BS-9049444', name='Enterprise One',
            enterprise_code='EAL-E/EO-MB/2301-01', business_type='SHOP')
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
        p_units = s_units
        baker.make(
            ItemUnits, item=item, sales_units=s_units, purchases_units=p_units,
            quantity_of_sale_units_per_purchase_unit=1, enterprise=enterprise_code)

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

        inventory_item = baker.make(InventoryItem, item=item, enterprise=enterprise_code)
        baker.make(
            InventoryInventoryItem, inventory=inventory, inventory_item=inventory_item)
        baker.make(
            InventoryRecord, inventory=inventory, inventory_item=inventory_item, record_type='ADD',
            quantity_recorded=20, unit_price=350, enterprise=enterprise_code)
        catalog_item = baker.make(
            CatalogItem, inventory_item=inventory_item, enterprise=enterprise_code)
        baker.make(
            CatalogCatalogItem, catalog=catalog, catalog_item=catalog_item,
            enterprise=enterprise_code)
        self.customer = baker.make(
            Customer, title='Mr', customer_number=9876, first_name='John',
            last_name='Wick', other_names='Baba Yaga', gender='MALE',
            phone_no='+254712345678', email='johnwick@parabellum.com', enterprise=enterprise_code)
        cart = baker.make(
            Cart, cart_code='EAS-C-10001', customer=self.customer, enterprise=enterprise_code)
        cart_item = baker.make(
            CartItem, cart=cart, catalog_item=catalog_item, quantity_added=2,
            enterprise=enterprise_code)
        order = baker.make(
            Order, customer=self.customer, cart_code=cart.cart_code, enterprise=enterprise_code)
        self.installment_order_item = baker.make(
            InstallmentsOrderItem, enterprise=enterprise_code,
            order=order, cart_item=cart_item,  confirmation_status='CONFIRMED',
            amount_paid=150, deposit_amount=150)
        next_installment_date = datetime.date.today() + datetime.timedelta(30)
        self.recipe = Recipe(
            Installment, installment_code='34567', installment_item=self.installment_order_item, amount=100,
            next_installment_date=next_installment_date,
            enterprise=enterprise_code)

    url = 'v1:orders:installment'

    def test_post(self, status_code=201):
        self.client = authenticate_test_user()
        test_post_data = self.post_data()
        test_post_data['installment_item'] = self.installment_order_item.id
        test_post_data['customer'] = self.customer.id
        url = reverse(self.url + '-list')
        OrderTransaction.objects.all().delete()
        Transaction.objects.all().delete()
        resp = self.client.post(url, test_post_data)
        assert resp.status_code == status_code, '{}, {}, {}'.format(resp.content, url, test_post_data)  # noqa

        assert Payment.objects.count() == 1
        payment = Payment.objects.first()
        assert payment.account_number == self.customer.phone_no
        assert payment.customer == self.customer
        assert payment.paid_amount == 100
        assert payment.final_amount == 100
        assert payment.balance_amount == 0
        assert payment.is_confirmed
        assert payment.is_installment
        assert payment.is_processed

        assert Transaction.objects.count() == 1
        transaction = Transaction.objects.first()
        assert transaction.account_number == self.customer.phone_no
        assert transaction.customer == self.customer
        assert transaction.amount == 100
        assert transaction.balance == 0
        assert transaction.transaction_means == 'CASH'
        assert transaction.transaction_type == 'DEPOSIT'
        assert transaction.is_processed

        assert payment.transaction_guid == transaction.id

        assert OrderTransaction.objects.count() == 1
        order_transaction = OrderTransaction.objects.first()
        assert order_transaction.amount == 100
        assert order_transaction.balance == 0
        assert order_transaction.is_installment
        assert order_transaction.order == self.installment_order_item.order
        assert order_transaction.transaction == transaction

        self.installment_order_item.refresh_from_db()
        assert self.installment_order_item.total_amount == 700
        assert self.installment_order_item.deposit_amount == 150
        assert self.installment_order_item.amount_due == 450
        assert self.installment_order_item.amount_paid == 150 + 100 == 250


    def test_put(self, status_code=200):
        self.client = authenticate_test_user()
        # First post
        test_post_data = self.post_data()
        test_post_data['installment_item'] = self.installment_order_item.id
        test_post_data['customer'] = self.customer.id
        url = reverse(self.url + '-list')
        OrderTransaction.objects.all().delete()
        Transaction.objects.all().delete()
        post_resp = self.client.post(url, test_post_data)

        # Now Put
        test_data = test_post_data
        test_data['amount'] = 200

        test_id = post_resp.data['id']
        url = reverse(
            self.url + '-detail', kwargs={self.id_field: test_id}
        )
        resp = self.client.put(url, test_data)

        assert resp.status_code == status_code, '{}, {}, {}'.format(resp.content, url, test_data)

        assert Payment.objects.count() == 1
        payment = Payment.objects.first()
        assert payment.account_number == self.customer.phone_no
        assert payment.customer == self.customer
        assert payment.paid_amount == 200
        assert payment.final_amount == 200
        assert payment.balance_amount == 0
        assert payment.is_confirmed
        assert payment.is_installment
        assert payment.is_processed

        assert Transaction.objects.count() == 1
        transaction = Transaction.objects.first()
        assert transaction.account_number == self.customer.phone_no
        assert transaction.customer == self.customer
        assert transaction.amount == 200
        assert transaction.balance == 0
        assert transaction.transaction_means == 'CASH'
        assert transaction.transaction_type == 'DEPOSIT'
        assert transaction.is_processed

        assert payment.transaction_guid == transaction.id

        assert OrderTransaction.objects.count() == 1
        order_transaction = OrderTransaction.objects.first()
        assert order_transaction.amount == 200
        assert order_transaction.balance == 0
        assert order_transaction.is_installment
        assert order_transaction.order == self.installment_order_item.order
        assert order_transaction.transaction == transaction

        self.installment_order_item.refresh_from_db()
        assert self.installment_order_item.total_amount == 700
        assert self.installment_order_item.deposit_amount == 150
        assert self.installment_order_item.total_installments == 200
        assert self.installment_order_item.amount_paid == 150 + 200 == 350
        assert self.installment_order_item.amount_due == 700 - 350 == 350

    def test_patch(self, status_code=200):
        pass
