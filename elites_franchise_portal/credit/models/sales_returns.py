"""Sales returns models file."""

from decimal import Decimal

from django.db import models
from django.core.validators import MinValueValidator

from elites_franchise_portal.items.models import Item
from elites_franchise_portal.common.models import AbstractBase
from elites_franchise_portal.debit.models import (
    InventoryRecord, InventoryItem, Sale, SaleRecord)
from elites_franchise_portal.restrictions_mgt.helpers import (
    get_valid_enterprise_setup_rules)


class SalesReturn(AbstractBase):
    """Sales returns model."""

    sale = models.ForeignKey(
        Sale, max_length=250, null=False, blank=False,
        on_delete=models.PROTECT)
    item = models.ForeignKey(
        Item, max_length=250, null=False, blank=False,
        on_delete=models.PROTECT)
    quantity_returned = models.FloatField(null=False, blank=False)
    unit_price = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=True, blank=True, default=0.0)
    total_price = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=True, blank=True)

    def save(self, *args, **kwargs):
        """Perform pre save and post save actions."""
        sale_record = SaleRecord.objects.filter(
            sale=self.sale, catalog_item__inventory_item__item=self.item).first()
        self.unit_price = self.unit_price or sale_record.selling_price if sale_record else 0
        self.total_price = round(
            Decimal(float(self.unit_price) * float(self.quantity_returned)), 2)
        super().save(*args, **kwargs)

        enterprise_setup_rules = get_valid_enterprise_setup_rules(self.enterprise)
        inventory = enterprise_setup_rules.default_inventory
        inventory_item = InventoryItem.objects.get(item=self.item, is_active=True)
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
                'record_type': 'ADD',
                'quantity_recorded': self.quantity_returned,
                'unit_price': Decimal(self.unit_price),
                'removal_guid': self.id,
            }
            InventoryRecord.objects.create(**inventory_record_payload, **audit_fields)

        else:
            inventory_record = inventory_records.first()
            inventory_record.inventory = inventory
            inventory_record.inventory_item = inventory_item
            inventory_record.record_type = 'ADD'
            inventory_record.quantity_recorded = self.quantity_returned
            inventory_record.unit_price = Decimal(self.unit_price)
            inventory_record.save()
