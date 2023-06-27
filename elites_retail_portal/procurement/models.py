"""Procurement models file."""

import datetime
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from elites_retail_portal.common.models import AbstractBase
from elites_retail_portal.enterprises.models import Enterprise, Staff
from elites_retail_portal.items.models import Item


def get_directory(instance, filename):
    """Determine the upload path for a file."""
    return "{}/{}_{}".format(
        instance.created_on.strftime("%Y/%m/%d"), instance.id, filename)


def add_lpos(x, y) -> str:
    """Add lpos."""
    return str(int(x) + int(y)).zfill(len(x))


class PurchaseOrder(AbstractBase):
    """Purchase order model."""

    lpo_date = models.DateTimeField(db_index=True, default=timezone.now)
    lpo_number = models.CharField(
        null=True, blank=True, max_length=300)
    supplier = models.ForeignKey(
        Enterprise, max_length=250, null=False, blank=False,
        related_name='purchaseorder_supplier', on_delete=models.PROTECT)
    description = models.TextField(null=True, blank=True)
    is_authorized = models.BooleanField(default=False)
    authorized_by = models.ForeignKey(
        Staff, null=True, blank=True, on_delete=models.PROTECT)

    @property
    def total_price(self):
        """Get total price."""
        purchase_order_items_totals = list(
            PurchaseOrderItem.objects.filter(
                purchase_order=self).values_list('total_price', flat=True))
        return sum(purchase_order_items_totals)

    def validate_unique_lpo_number(self):
        """Validate unique lpo number."""
        if self.__class__.objects.filter(
                enterprise=self.enterprise,
                lpo_number=self.lpo_number).exclude(id=self.id).exists():
            msg = "A Local Purchase Order with this LPO number already exists. "\
                "Please assign a different LPO number for this order"
            raise ValidationError({'lpo_number': msg})

    def authorize(self, user=None):
        """Authorize the lpo."""
        if not user:
            user = get_user_model().objects.filter(id=self.updated_by).first()
            if not user:
                msg = "You do not exist as a user"
                raise ValidationError({'authorization': msg})

        authorizer = Staff.objects.filter(email=user.email).first()
        if not authorizer:
            msg = "You are not registered as a staff"
            raise ValidationError({'authorization': msg})

        self.is_authorized = True
        self.authorized_by = authorizer
        self.save()

        purchase_order_items = PurchaseOrderItem.objects.filter(purchase_order=self)
        if purchase_order_items.exists():
            for purchase_order_item in purchase_order_items:
                purchase_order_item.is_authorized = True
                purchase_order_item.authorized_by = authorizer
                purchase_order_item.save()
        return

    def create_lpo_number(self):
        """Create an LPO number."""
        if not self.lpo_number:
            year = datetime.datetime.today().year
            lpos = self.__class__.objects.filter(enterprise=self.enterprise).exclude(id=self.id)
            if not lpos.exists():
                self.lpo_number = "{}-00000".format(str(year)[-2:])
                return

            latest_lpo = lpos.latest('lpo_date')
            new_number = add_lpos(latest_lpo.lpo_number.split('-')[1], '1')
            new_lpo_num = "{}-{}".format(str(year)[-2:], new_number)
            if not self.__class__.objects.filter(
                    enterprise=self.enterprise,
                    lpo_number=new_lpo_num).exclude(id=self.id).exists():
                self.lpo_number = new_lpo_num
                return

    def clean(self) -> None:
        """Perform clean actions."""
        self.validate_unique_lpo_number()
        return super().clean()

    def save(self, *args, **kwargs):
        """Save action."""
        self.create_lpo_number()
        return super().save(*args, **kwargs)


class PurchaseOrderScan(AbstractBase):
    """."""

    purchase_order = models.ForeignKey(
        PurchaseOrder, max_length=250, null=False, blank=False, on_delete=models.PROTECT)
    lpo_scan = models.FileField(upload_to=get_directory, null=True, blank=True)


class PurchaseOrderItem(AbstractBase):
    """Purchase Order Item."""

    purchase_order = models.ForeignKey(
        PurchaseOrder, max_length=250, null=False, blank=False, on_delete=models.PROTECT)
    item = models.ForeignKey(
        Item, null=False, blank=False, on_delete=models.PROTECT)
    unit_price = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=False, blank=False)
    quantity = models.FloatField(null=False, blank=False)
    total_price = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=True, blank=True)
    is_authorized = models.BooleanField(default=False)
    authorized_by = models.ForeignKey(
        Staff, null=True, blank=True, on_delete=models.PROTECT)
    description = models.TextField(null=True, blank=True)

    def get_total_price(self):
        """Get total price."""
        self.total_price = Decimal(float(self.unit_price) * float(self.quantity))

    def authorize_item(self, user=None):
        """Authorize the lpo."""
        if not user:
            user = get_user_model().objects.filter(id=self.updated_by).first()
            if not user:
                msg = "You do not exist as a user"
                raise ValidationError({'authorization': msg})

        authorizer = Staff.objects.filter(email=user.email).first()
        if not authorizer:
            msg = "You are not registered as a staff"
            raise ValidationError({'authorization': msg})

        self.is_authorized = True
        self.authorized_by = authorizer
        self.save()

        if not self.__class__.objects.filter(
                purchase_order=self.purchase_order, is_authorized=False).exists():
            self.purchase_order.is_authorized = True
            self.purchase_order.authorized_by = authorizer
            self.purchase_order.save()

    def save(self, *args, **kwargs):
        """."""
        self.get_total_price()
        return super().save(*args, **kwargs)
