"""."""
import pytest
from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase
from tests.utils.api import APITests

from elites_retail_portal.enterprises.models import Enterprise
from elites_retail_portal.items.models import (
    Brand, BrandItemType, Category, Item, ItemModel, ItemType,
    ItemUnits, UnitsItemType, Units, Product)
from elites_retail_portal.warehouses.models import Warehouse
from elites_retail_portal.credit.models import (
    Purchase, PurchaseItem, PurchasePayment)
from elites_retail_portal.debit.models import (
    Inventory, InventoryInventoryItem, InventoryItem)
from tests.utils.login_mixins import authenticate_test_user
from elites_retail_portal.catalog.models import Catalog
from elites_retail_portal.enterprise_mgt.models import (
    EnterpriseSetupRule, EnterpriseSetupRuleInventory,
    EnterpriseSetupRuleCatalog, EnterpriseSetupRuleWarehouse)
from django.urls import reverse
from model_bakery import baker
from model_bakery.recipe import Recipe


class TestPurchasesView(APITests, APITestCase):
    """."""

    def setUp(self):
        """."""
        franchise = baker.make(
            Enterprise, name='Enterprise One', enterprise_code='EAL-E/EO-MB/2301-01',
            business_type='SHOP')
        enterprise_code = franchise.enterprise_code
        supplier = baker.make(Enterprise, name='LG Supplier')
        self.recipe = Recipe(
            Purchase, invoice_number='INV-001', supplier=supplier, enterprise=enterprise_code)

    url = 'v1:credit:purchase'


class TestPurchasePaymentsView(APITests, APITestCase):
    """."""

    def setUp(self):
        """."""
        franchise = baker.make(
            Enterprise, name='Enterprise One', enterprise_code='EAL-E/EO-MB/2301-01',
            business_type='SHOP')
        enterprise_code = franchise.enterprise_code
        supplier = baker.make(Enterprise, name='LG Supplier')
        purchase = baker.make(
            Purchase, invoice_number='INV-001', supplier=supplier, enterprise=enterprise_code)
        self.recipe = Recipe(
            PurchasePayment, purchase=purchase, payment_method="CASH", amount=5000, enterprise=enterprise_code)
    url = 'v1:credit:purchasepayment'


class TestPurchaseItemsView(APITests, APITestCase):
    """."""

    def setUp(self):
        """."""
        franchise = baker.make(
            Enterprise, name='Enterprise One', enterprise_code='EAL-E/EO-MB/2301-01',
            business_type='SHOP')
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
        inventory = baker.make(
            Inventory, inventory_name='Elites Age Supermarket Available Inventory',
            is_default=True,
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
        supplier = baker.make(Enterprise, name='LG Supplier')
        purchase = baker.make(
            Purchase, invoice_number='INV-001', supplier=supplier, enterprise=enterprise_code)
        item.activate()
        self.recipe = Recipe(
            PurchaseItem, purchase=purchase, item=item, quantity_purchased=10, total_cost=10000,
            recommended_retail_price=100, quantity_to_inventory=5,
            quantity_to_inventory_on_display=4, enterprise=enterprise_code)

    url = 'v1:credit:purchaseitem'

    def test_post(self, status_code=201):
        """."""
        self.client = authenticate_test_user()
        purchase_item = self.make()
        PurchaseItem.objects.all().delete()
        test_data = self.get_test_data(purchase_item)
        url = reverse(self.url + '-list')
        resp = self.client.post(url, test_data)
        assert resp.status_code == status_code, '{}, {}, {}'.format(resp.content, url, test_data)  # noqa
        if resp.status_code != 201:
            return resp
        self.compare_dicts(test_data, resp.data)

        return test_data, resp

    def test_post_with_product_codes(self, status_code=201):
        """."""
        self.client = authenticate_test_user()
        purchase_item = self.make()
        PurchaseItem.objects.all().delete()
        test_data = self.get_test_data(purchase_item)
        baker.make(Product, serial_number=123456, item=purchase_item.item, enterprise=purchase_item.enterprise)
        test_data['serial_numbers'] = [123456, 987654, 546372]
        url = reverse(self.url + '-list')
        resp = self.client.post(url, test_data)
        assert resp.status_code == 400
        msg = "A product with the serial number 123456 already exists"
        assert msg in resp.data['serial_number']

        Product.objects.all().delete()

        resp = self.client.post(url, test_data)
        assert resp.status_code == status_code
        Product.objects.count() == 3
        return test_data, resp

    def test_patch(self, status_code=200):
        """."""
        self.client = authenticate_test_user()
        instance = self.make()
        test_data = self.get_test_data(instance)
        test_id = getattr(instance, self.id_field)
        assert test_id, test_id
        assert instance.__class__.objects.get(pk=test_id), \
            'unable to get instance with PK {}'.format(test_id)
        url = reverse(
            self.url + '-detail', kwargs={self.id_field: test_id}
        )
        resp = self.client.patch(url, test_data)
        assert resp.status_code == status_code, '{}, {}, {}'.format(resp.content, url, test_data)
        return resp

    def test_put(self, status_code=200):
        """."""
        self.client = authenticate_test_user()

        instance = self.make()
        test_data = self.get_test_data(instance)

        test_id = getattr(instance, self.id_field)
        url = reverse(
            self.url + '-detail', kwargs={self.id_field: test_id}
        )

        resp = self.client.put(url, test_data)
        assert resp.status_code == status_code, '{}, {}, {}'.format(resp.content, url, test_data)
        return resp


    def test_put_with_product_codes(self, status_code=200):
        """."""
        self.client = authenticate_test_user()

        instance = self.make()
        test_data = self.get_test_data(instance)
        baker.make(Product, serial_number=123456, item=instance.item, enterprise=instance.enterprise)
        test_data['serial_numbers'] = [123456, 987654, 546372]

        test_id = getattr(instance, self.id_field)
        url = reverse(
            self.url + '-detail', kwargs={self.id_field: test_id}
        )

        resp = self.client.put(url, test_data)
        assert resp.status_code == status_code, '{}, {}, {}'.format(resp.content, url, test_data)
        return resp
