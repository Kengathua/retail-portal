"""Sales model file."""

from decimal import Decimal
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.core.validators import MinValueValidator

from elites_retail_portal.common.models import AbstractBase
from elites_retail_portal.catalog.models import CatalogItem
from elites_retail_portal.customers.models import Customer
from django.contrib.auth import get_user_model
from elites_retail_portal.debit.models import InventoryRecord
from elites_retail_portal.orders.models.orders import Order
from elites_retail_portal.encounters.models import Encounter
from elites_retail_portal.enterprise_mgt.helpers import get_valid_enterprise_setup_rules

SALE_TYPE_CHOICES = (
    ('INSTANT', 'INSTANT'),
    ('INSTALLMENT', 'INSTALLMENT'),
)

SALE_RECORD_PROCESSING_STATUS_CHOICES = (
    ('PENDING', 'PENDING'),
    ('CANCELED', 'CANCELED'),
    ('REJECTED', 'REJECTED'),
    ('CONFIRMED', 'CONFIRMED'),
    ('PROCESSED', 'PROCESSED'),
)

PENDING = 'PENDING'
INSTANT = 'INSTANT'
INSTALLMENT = 'INSTALLMENT'


class Sale(AbstractBase):
    """Sales model."""

    sale_date = models.DateTimeField(db_index=True, default=timezone.now)
    customer = models.ForeignKey(
        Customer, null=True, blank=True, on_delete=models.PROTECT)
    sale_code = models.CharField(null=True, blank=True, max_length=300)
    order = models.ForeignKey(Order, null=True, blank=True, on_delete=models.PROTECT)
    total_amount = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=True, blank=True, default=0)
    data = models.JSONField(null=True, blank=True)
    receipt_number = models.CharField(null=True, blank=True, max_length=300)
    is_active = models.BooleanField(default=True)
    is_cleared = models.BooleanField(default=False)

    @property
    def sale_summary(self):
        """Generate a summary for the sale."""
        pass

    def get_receipt_number(self):
        """Get the receipt number."""
        encounter = Encounter.objects.filter(order_guid=self.order.id).first()
        if encounter:
            self.receipt_number = encounter.receipt_number

    def check_customer(self):
        """Check customer."""
        if not self.customer:
            user = get_user_model().objects.filter(
                Q(id=self.created_by) | Q(id=self.updated_by) | Q(
                    guid=self.created_by) | Q(guid=self.updated_by))
            if user.exists():
                user = user.first()
                customer = Customer.objects.filter(enterprise_user=user)
                if customer.exists():
                    customer = customer.first()
                    self.customer = customer

    def check_cart(self):
        """Check cart exists."""
        from elites_retail_portal.orders.models import Cart
        if not self.__class__.objects.filter(id=self.id).exists():
            # Sale is not yet created
            carts = Cart.objects.filter(
                sale=self, customer=self.customer, is_empty=True, is_active=True,
                is_checked_out=False)
        else:
            carts = Cart.objects.filter(
                sale=self, customer=self.customer, is_active=True,
                is_checked_out=False)

        if not carts.exists():
            cart_payload = {
                'customer': self.customer,
                'is_active': True,
                'is_checked_out': False,
                'created_by': self.created_by,
                'updated_by': self.updated_by,
                'franchise': self.enterprise,
                'sale': self,
                'is_empty': True,
            }
            Cart.objects.create(**cart_payload)

    def save(self, *args, **kwargs):
        """Perform pre save and post save actions."""
        self.check_customer()
        self.get_receipt_number()
        super().save(*args, **kwargs)
        # self.check_cart()


class SaleItem(AbstractBase):
    """Sales item model."""

    sale = models.ForeignKey(
        Sale, verbose_name=("sales"), on_delete=models.PROTECT)
    catalog_item = models.ForeignKey(
        CatalogItem, null=False, blank=False,
        on_delete=models.PROTECT)
    sale_type = models.CharField(
        max_length=300, choices=SALE_TYPE_CHOICES, default=INSTANT)
    selling_price = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=True, blank=True, default=0)
    total_amount = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=True, blank=True, default=0)
    amount_paid = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=True, blank=True, default=0)
    quantity_sold = models.FloatField()
    processing_status = models.CharField(
        max_length=300, choices=SALE_RECORD_PROCESSING_STATUS_CHOICES,
        default=PENDING)
    is_cleared = models.BooleanField(default=False)

    @property
    def unit_price(self):
        """Get unit price."""
        pass

    def clean(self) -> None:
        """Clean sale model."""
        super().clean()

    def save(self, *args, **kwargs):
        """Perform pre save and post save actions."""
        self.total_amount = Decimal(float(self.selling_price) * self.quantity_sold)
        super().save(*args, **kwargs)
        enterprise_setup_rules = get_valid_enterprise_setup_rules(self.enterprise)
        default_inventory = enterprise_setup_rules.default_inventory
        inventory_item = self.catalog_item.inventory_item
        audit_fields = {
            'created_by': self.created_by,
            'updated_by': self.updated_by,
            'enterprise': self.enterprise,
        }

        record = InventoryRecord.objects.filter(removal_guid=self.id).first()
        if record:
            record.inventory_item = inventory_item
            record.quantity_recorded = self.quantity_sold
            record.unit_price = self.selling_price
            record.quantity_sold = self.quantity_sold
            record.save()
        else:
            InventoryRecord.objects.create(
                inventory=default_inventory, inventory_item=inventory_item,
                quantity_recorded=self.quantity_sold, unit_price=self.selling_price,
                quantity_sold=self.quantity_sold, record_type='REMOVE',
                removal_type='SALES', removal_guid=self.id, **audit_fields)
