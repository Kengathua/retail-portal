"""Sales model file."""

from decimal import Decimal
from django.db import models
from django.db.models import Q
from django.core.validators import MinValueValidator
from django.contrib.postgres.fields import ArrayField

from elites_franchise_portal.common.models import AbstractBase
from elites_franchise_portal.catalog.models import CatalogItem
from elites_franchise_portal.customers.models import Customer
from django.contrib.auth import get_user_model

from elites_franchise_portal.orders.models.orders import Order

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

    customer = models.ForeignKey(
        Customer, null=True, blank=True, on_delete=models.PROTECT)
    sale_code = models.CharField(null=True, blank=True, max_length=300)
    order = models.ForeignKey(Order, null=True, blank=True, on_delete=models.PROTECT)
    total_amount = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=True, blank=True, default=0)
    encounter = models.JSONField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_cleared = models.BooleanField(default=False)

    @property
    def sale_summary(self):
        """Generate a summary for the sale."""
        pass

    def check_customer(self):
        if not self.customer:
            user = get_user_model().objects.filter(
                Q(id=self.created_by)| Q(id=self.updated_by) | Q(
                    guid=self.created_by)| Q(guid=self.updated_by))
            if user.exists():
                user = user.first()
                customer = Customer.objects.filter(franchise_user=user)
                if customer.exists():
                    customer = customer.first()
                    self.customer = customer

    def check_cart(self):
        """Check cart exists."""
        from elites_franchise_portal.orders.models import Cart
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
                'franchise': self.franchise,
                'sale': self,
                'is_empty':True,
            }
            Cart.objects.create(**cart_payload)

    def save(self, *args, **kwargs):
        """Perform pre save and post save actions."""
        self.check_customer()
        super().save(*args, **kwargs)
        # self.check_cart()


class SaleRecord(AbstractBase):
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
    amount_paid = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=True, blank=True, default=0)
    quantity_sold = models.FloatField()
    opening_stock_quantity = models.FloatField(null=True, blank=True, default=0)
    closing_stock_quantity = models.FloatField(null=True, blank=True, default=0)
    opening_stock_amount = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=True, blank=True, default=0)
    closing_stock_amount = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=True, blank=True, default=0)
    processing_status = models.CharField(
        max_length=300, choices=SALE_RECORD_PROCESSING_STATUS_CHOICES,
        default=PENDING)
    is_cleared = models.BooleanField(default=False)

    @property
    def unit_price(self):
        """Get unit price."""
        pass

    def get_opening_stock(self):
        """Get opening stock."""
        self.opening_stock_quantity = self.catalog_item.inventory_item.summary['available_quantity'] or 0   # noqa
        self.opening_stock_amount = self.catalog_item.inventory_item.summary['total'] or 0

    def get_closing_stock(self):
        """Get opening stock."""
        item_sold_total = self.quantity_sold * Decimal(self.selling_price)
        self.closing_stock_quantity = self.opening_stock_quantity + self.quantity_sold
        self.closing_stock_amount = self.opening_stock_amount + item_sold_total

    def clean(self) -> None:
        """Clean sale model."""
        super().clean()

    def save(self, *args, **kwargs):
        """Perform pre save and post save actions."""
        self.get_opening_stock()
        self.get_closing_stock()
        super().save(*args, **kwargs)
