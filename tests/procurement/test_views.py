"""."""

import uuid
import pytest
import tempfile
from PIL import Image

from django.urls import reverse
from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework.test import APITestCase

from elites_retail_portal.enterprises.models import Enterprise, Staff
from elites_retail_portal.items.models import (
    Brand, BrandItemType, Category, Item, ItemModel, ItemType)
from elites_retail_portal.procurement.models import (
    PurchaseOrder, PurchaseOrderItem, PurchaseOrderScan)
from elites_retail_portal.credit.models import Purchase
from tests.utils.api import APITests
from tests.utils.login_mixins import authenticate_test_user

from model_bakery import baker
from model_bakery.recipe import Recipe


def temporary_scan_file():
    """."""
    from io import BytesIO
    bts = BytesIO()
    img = Image.new("RGB", (100, 100))
    img.save(bts, 'jpeg')
    return SimpleUploadedFile("test.jpg", bts.getvalue())


class TestPurchaseOrderView(APITests, APITestCase):
    """."""

    def setUp(self):
        """."""
        enterprise = baker.make(
            Enterprise, name='Enterprise One', enterprise_type='FRANCHISE')
        self.enterprise_code = enterprise.enterprise_code
        self.supplier = baker.make(Enterprise, name='LG Supplier')
        lpo_date = timezone.now()
        self.recipe = Recipe(
            PurchaseOrder, lpo_date=lpo_date, lpo_number="LPO-001",
            supplier=self.supplier, description="Seeking to purchase a Samsung cooker",
            enterprise=self.enterprise_code)

    url = 'v1:procurement:purchaseorder'

    def test_create_purchase(self, expected_code=201):
        """."""
        self.client = authenticate_test_user()
        for model in self.get_model()._meta.related_objects:
            model.related_model.objects.all().delete()
        self.get_model().objects.all().delete()
        instance = self.make()
        url = reverse(self.url + '-list') + "{}/create_purchase/".format(instance.id)
        payload = {
            "invoice_number": "INV-001"
        }
        assert not Purchase.objects.count()
        resp = self.client.post(url, payload)
        assert resp.status_code == expected_code == 201
        assert Purchase.objects.count() == 1


class TestPurchaseOrderScanView(APITests, APITestCase):
    """."""

    def setUp(self):
        """."""
        enterprise = baker.make(
            Enterprise, name='Enterprise One', enterprise_type='FRANCHISE')
        self.enterprise_code = enterprise.enterprise_code
        self.supplier = baker.make(Enterprise, name='LG Supplier')
        lpo_date = timezone.now()
        purchase_order = baker.make(
            PurchaseOrder, lpo_date=lpo_date, lpo_number="LPO-001",
            supplier=self.supplier, description="Seeking to purchase a Samsung cooker",
            enterprise=self.enterprise_code)
        self.recipe = Recipe(
            PurchaseOrderScan, purchase_order=purchase_order,
            lpo_scan=temporary_scan_file(), enterprise=self.enterprise_code)

    url = 'v1:procurement:purchaseorderscan'

    def test_put(self, status_code=201):
        """."""
        pass

    def test_patch(self, status_code=200):
        """."""
        pass


class TestPurchaseOrderItemView(APITests, APITestCase):
    """."""

    def setUp(self):
        """."""
        enterprise = baker.make(
            Enterprise, name='Enterprise One', enterprise_type='FRANCHISE')
        self.enterprise_code = enterprise.enterprise_code
        self.supplier = baker.make(Enterprise, name='LG Supplier')
        cat = baker.make(
            Category, category_name='Cat One',
            enterprise=self.enterprise_code)
        item_type = baker.make(
            ItemType, category=cat, type_name='Cooker',
            enterprise=self.enterprise_code)
        brand = baker.make(
            Brand, brand_name='Samsung', enterprise=self.enterprise_code)
        baker.make(
            BrandItemType, brand=brand, item_type=item_type,
            enterprise=self.enterprise_code)
        item_model = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731K-B SUT',
            enterprise=self.enterprise_code)
        item = baker.make(
            Item, item_model=item_model, barcode='83838388383', make_year=2020,
            enterprise=self.enterprise_code)
        lpo_date = timezone.now()
        purchase_order = baker.make(
            PurchaseOrder, lpo_date=lpo_date, lpo_number="LPO-001",
            supplier=self.supplier, description="Seeking to purchase a Samsung cooker",
            enterprise=self.enterprise_code)
        self.recipe = Recipe(
            PurchaseOrderItem, purchase_order=purchase_order,
            item=item, quantity=5, unit_price=60000,
            description="Seeking to purchase a Samsung cooker",
            enterprise=self.enterprise_code)

    url = 'v1:procurement:purchaseorderitem'
