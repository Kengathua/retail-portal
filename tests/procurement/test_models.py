"""."""
import uuid
import pytest
import datetime

from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError

from elites_retail_portal.enterprises.models import Enterprise, Staff
from elites_retail_portal.items.models import (
    Brand, BrandItemType, Category, Item, ItemModel, ItemType)
from elites_retail_portal.procurement.models import (
    PurchaseOrder, PurchaseOrderItem, PurchaseOrderScan)
from elites_retail_portal.users.models import User

from model_bakery import baker
from model_bakery.recipe import Recipe


class TestPurchaseOrder(TestCase):
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
        self.item = baker.make(
            Item, item_model=item_model, barcode='83838388383', make_year=2020,
            enterprise=self.enterprise_code)

    def test_create_purchase_order(self):
        """."""
        lpo_date = timezone.now()
        purchase_order = baker.make(
            PurchaseOrder, lpo_date=lpo_date, lpo_number="LPO-001",
            supplier=self.supplier, description="Seeking to purchase a Samsung cooker",
            enterprise=self.enterprise_code)
        purchase_order.save()

        assert purchase_order.total_price == 0
        assert PurchaseOrder.objects.count() == 1

    def test_validate_unique_lpo_number(self):
        """Validate unique lpo number."""
        lpo_date1 = timezone.now()
        baker.make(
            PurchaseOrder, lpo_date=lpo_date1, lpo_number="LPO-001",
            supplier=self.supplier, description="Seeking to purchase a Samsung cooker",
            enterprise=self.enterprise_code)
        lpo_date2 = timezone.now()
        purchase_order = Recipe(
            PurchaseOrder, lpo_date=lpo_date2, lpo_number="LPO-001",
            supplier=self.supplier, description="Seeking to purchase a Samsung cooker",
            enterprise=self.enterprise_code)

        with pytest.raises(ValidationError) as ve:
            purchase_order.make()
        msg = 'A Local Purchase Order with this LPO number already exists. '\
            'Please assign a different LPO number for this order'
        assert msg in ve.value.messages

    def test_authorize_purchase_order(self):
        """."""
        lpo_date = timezone.now()
        purchase_order = baker.make(
            PurchaseOrder, lpo_date=lpo_date, lpo_number="LPO-001",
            supplier=self.supplier, description="Seeking to purchase a Samsung cooker",
            enterprise=self.enterprise_code)
        with pytest.raises(ValidationError) as ve:
            purchase_order.authorize()
        msg = 'You do not exist as a user'
        assert msg in ve.value.messages
        user = baker.make(
            User, email='testuser@email.com', first_name='Test', last_name='User',
            guid=uuid.uuid4(), enterprise=self.enterprise_code)
        purchase_order.updated_by = user.id
        purchase_order.save()

        with pytest.raises(ValidationError) as ve:
            purchase_order.authorize()
        msg = 'You are not registered as a staff'
        assert msg in ve.value.messages

        with pytest.raises(ValidationError) as ve:
            purchase_order.authorize(user)
        msg = 'You are not registered as a staff'
        assert msg in ve.value.messages

        staff = baker.make(
            Staff,  email=user.email, first_name="Staff", last_name="Name",
            staff_number="1011")
        purchase_order.authorize(user)

        purchase_order.refresh_from_db()
        assert purchase_order.is_authorized
        assert purchase_order.authorized_by == staff

        purchase_order_item = baker.make(
            PurchaseOrderItem, purchase_order=purchase_order,
            item=self.item, quantity=5, unit_price=60000,
            description="Seeking to purchase a Samsung cooker",
            enterprise=self.enterprise_code)
        purchase_order_item.refresh_from_db()
        assert not purchase_order_item.is_authorized
        purchase_order.authorize(user)
        purchase_order_item.refresh_from_db()
        assert purchase_order_item.is_authorized

    def test_create_lpo_number(self):
        """."""
        lpo_date = timezone.now()
        purchase_order1 = baker.make(
            PurchaseOrder, lpo_date=lpo_date,
            supplier=self.supplier, description="Seeking to purchase Samsung cookers",
            enterprise=self.enterprise_code)
        year = datetime.datetime.today().year
        purchase_order1.refresh_from_db()
        assert purchase_order1.lpo_number == f'{str(year)[-2:]}-00000'
        purchase_order1.save()
        purchase_order1.refresh_from_db()
        assert purchase_order1.lpo_number == f'{str(year)[-2:]}-00000'

        purchase_order2 = baker.make(
            PurchaseOrder, lpo_date=lpo_date,
            supplier=self.supplier, description="Seeking to purchase another round of Samsung cookers",
            enterprise=self.enterprise_code)
        purchase_order2.refresh_from_db()
        assert purchase_order2.lpo_number == f'{str(year)[-2:]}-00001'
        purchase_order2.save()
        purchase_order2.refresh_from_db()
        assert purchase_order2.lpo_number == f'{str(year)[-2:]}-00001'

        purchase_order1.save()
        purchase_order1.refresh_from_db()
        assert purchase_order1.lpo_number == f'{str(year)[-2:]}-00000'

class TestPurchaseOrderScan(TestCase):
    """."""

    def setUp(self) -> None:
        """."""
        enterprise = baker.make(
            Enterprise, name='Enterprise One', enterprise_type='FRANCHISE')
        self.enterprise_code = enterprise.enterprise_code
        self.supplier = baker.make(Enterprise, name='LG Supplier')

    def test_create_purchase_order_scan(self):
        """."""
        lpo_date = timezone.now()
        purchase_order = baker.make(
            PurchaseOrder, lpo_date=lpo_date, lpo_number="LPO-001",
            supplier=self.supplier, description="Seeking to purchase a Samsung cooker",
            enterprise=self.enterprise_code)
        purchase_order_lpo_scan = baker.make(
            PurchaseOrderScan, purchase_order=purchase_order, lpo_scan='file.png')

        assert purchase_order_lpo_scan
        assert PurchaseOrderScan.objects.count() == 1


class TestPurchaseOrderItem(TestCase):
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
        self.item = baker.make(
            Item, item_model=item_model, barcode='83838388383', make_year=2020,
            enterprise=self.enterprise_code)

    def test_create_purchase_order_item(self):
        """."""
        lpo_date = timezone.now()
        purchase_order = baker.make(
            PurchaseOrder, lpo_date=lpo_date, lpo_number="LPO-001",
            supplier=self.supplier, description="Seeking to purchase a Samsung cooker",
            enterprise=self.enterprise_code)
        purchase_order_item = baker.make(
            PurchaseOrderItem, purchase_order=purchase_order,
            item=self.item, quantity=5, unit_price=60000,
            description="Seeking to purchase a Samsung cooker",
            enterprise=self.enterprise_code)

        assert purchase_order.total_price == 300000
        assert purchase_order_item.total_price == 300000
        assert PurchaseOrderItem.objects.count() == 1

    def test_authorize_purchase_order_item(self):
        """."""
        lpo_date = timezone.now()
        purchase_order = baker.make(
            PurchaseOrder, lpo_date=lpo_date, lpo_number="LPO-001",
            supplier=self.supplier, description="Seeking to purchase a Samsung cooker",
            enterprise=self.enterprise_code)
        purchase_order_item = baker.make(
            PurchaseOrderItem, purchase_order=purchase_order,
            item=self.item, quantity=5, unit_price=60000,
            description="Seeking to purchase a Samsung cooker",
            enterprise=self.enterprise_code)
        with pytest.raises(ValidationError) as ve:
            purchase_order_item.authorize_item()
        msg = 'You do not exist as a user'
        assert msg in ve.value.messages
        user = baker.make(
            User, email='testuser@email.com', first_name='Test', last_name='User',
            guid=uuid.uuid4(), enterprise=self.enterprise_code)
        purchase_order_item.updated_by = user.id
        purchase_order_item.save()

        with pytest.raises(ValidationError) as ve:
            purchase_order_item.authorize_item()
        msg = 'You are not registered as a staff'
        assert msg in ve.value.messages

        with pytest.raises(ValidationError) as ve:
            purchase_order_item.authorize_item(user)
        msg = 'You are not registered as a staff'
        assert msg in ve.value.messages

        staff = baker.make(
            Staff,  email=user.email, first_name="Staff", last_name="Name",
            staff_number="1011")
        purchase_order_item.authorize_item(user)

        purchase_order_item.refresh_from_db()
        assert purchase_order_item.is_authorized
        assert purchase_order_item.authorized_by == staff
