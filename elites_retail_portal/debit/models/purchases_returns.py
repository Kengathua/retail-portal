"""."""

from decimal import Decimal

from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

from elites_retail_portal.credit.models import PurchaseItem
from elites_retail_portal.common.models import AbstractBase
from elites_retail_portal.debit.models import InventoryRecord, InventoryItem
from elites_retail_portal.enterprise_mgt.helpers import get_valid_enterprise_setup_rules


class PurchasesReturn(AbstractBase):
    """Purchases Returns model."""

    purchase_item = models.ForeignKey(
        PurchaseItem, max_length=250, null=False, blank=False,
        on_delete=models.PROTECT)
    quantity_returned = models.FloatField(null=False, blank=False)
    unit_price = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=True, blank=True, default=0.0)
    total_price = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    return_date = models.DateTimeField(db_index=True, default=timezone.now)

    @property
    def purchase(self):
        """Purchase property."""
        return self.purchase_item.purchase or None

    def validate_unique_return_item_per_purchase(self):
        """Validate unique return item per purchase."""
        if self.__class__.objects.filter(
                purchase_item=self.purchase_item).exclude(id=self.id).exists():
            msg = "The item {} already exists as a returned item. '\
                'Kindly select Edit to update it".format(
                    self.purchase_item.item.item_name)
            raise ValidationError({'update_item': msg})

    def validate_quantity_returned_less_than_quantity_purchased(self):
        """."""
        if self.quantity_returned > self.purchase_item.quantity_purchased:
            msg = 'The quantity purchased {} is less than the quantity returned {}'.format(
                self.purchase_item.quantity_purchased, self.quantity_returned)
            raise ValidationError(
                {'quantity_returned': msg})

    def clean(self) -> None:
        """Clean purchase return."""
        self.validate_unique_return_item_per_purchase()
        self.validate_quantity_returned_less_than_quantity_purchased()
        return super().clean()

    def save(self, *args, **kwargs):
        """Pre save and post save actions."""
        self.unit_price = self.unit_price or self.purchase_item.unit_price
        self.total_price = round(
            Decimal(float(self.unit_price) * float(self.quantity_returned)), 2)
        super().save(*args, **kwargs)
        enterprise_setup_rules = get_valid_enterprise_setup_rules(self.enterprise)
        inventory = enterprise_setup_rules.default_inventory
        inventory_item = InventoryItem.objects.get(item=self.purchase_item.item, is_active=True)
        audit_fields = {
            'created_by': self.created_by,
            'updated_by': self.updated_by,
            'enterprise': self.enterprise,
        }

        inventory_records = InventoryRecord.objects.filter(removal_guid=self.id)

        if not inventory_records.exists():
            inventory_record_payload = {
                'inventory': inventory,
                'inventory_item': inventory_item,
                'record_type': 'REMOVE',
                'removal_type': 'PURCHASES RETURNS',
                'quantity_recorded': self.quantity_returned,
                'unit_price': Decimal(self.unit_price),
                'removal_guid': self.id,
            }
            InventoryRecord.objects.create(**inventory_record_payload, **audit_fields)

        else:
            inventory_record = inventory_records.first()
            inventory_record.inventory = inventory
            inventory_record.inventory_item = inventory_item
            inventory_record.record_type = 'REMOVE'
            inventory_record.removal_type = 'PURCHASES RETURNS'
            inventory_record.quantity_recorded = self.quantity_returned
            inventory_record.unit_price = Decimal(self.unit_price)
            inventory_record.save()
