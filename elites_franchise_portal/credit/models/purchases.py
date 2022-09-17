"""Purchases models file."""

import decimal

from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator

from elites_franchise_portal.common.models import AbstractBase
from elites_franchise_portal.warehouses.models import (
    Warehouse, WarehouseItem, WarehouseRecord)
from elites_franchise_portal.items.models import Item, ItemUnits
from elites_franchise_portal.enterprises.models import Enterprise


class Purchase(AbstractBase):
    """Purchases model."""

    supplier = models.ForeignKey(
        Enterprise, max_length=250, null=False, blank=False,
        related_name='supplier_enterprise', on_delete=models.PROTECT)
    invoice_number = models.CharField(
        null=True, blank=True, max_length=300)
    item = models.ForeignKey(
        Item, null=False, blank=False, on_delete=models.PROTECT)
    quantity_purchased = models.FloatField(null=False, blank=False)
    sale_units_purchased = models.FloatField(null=True, blank=True)
    total_price = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=False, blank=False)
    unit_price = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=True, blank=True, default=0.0)
    recommended_retail_price = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=True, blank=True, default=0.0)
    purchase_date = models.DateTimeField(db_index=True, default=timezone.now)
    quantity_to_inventory = models.FloatField(null=True, blank=True)
    quantity_to_inventory_on_display = models.FloatField(null=True, blank=True)
    quantity_to_inventory_in_warehouse = models.FloatField(null=True, blank=True)
    move_in_bulk = models.BooleanField(default=False)

    def get_unit_price(self):
        """Calculate buying price per unit."""
        total_no_of_items = self.sale_units_purchased
        buying_price = decimal.Decimal(
            float(self.total_price) / total_no_of_items).quantize(
                decimal.Decimal('0.00'), rounding=decimal.ROUND_CEILING)

        self.unit_price = buying_price

    def get_total_no_of_items(self):
        """Get the total number selling units eg 12 packets from a dozen purchased."""
        if not self.sale_units_purchased:
            item_units = ItemUnits.objects.filter(item=self.item).first()
            no_of_sale_quantity_of_sale_units_per_purchase_unit = item_units.quantity_of_sale_units_per_purchase_unit
            total_no_of_items = no_of_sale_quantity_of_sale_units_per_purchase_unit * self.quantity_purchased
            self.sale_units_purchased = total_no_of_items

    def validate_item_has_units_registered_to_it(self):
        """Validate that the items purchased have units to measure them."""
        from elites_franchise_portal.items.models import ItemUnits
        if not ItemUnits.objects.filter(item=self.item).exists():
            raise ValidationError(
                {'item_units': 'Please register the units used to record this item'})

    def clean(self) -> None:
        """Clean the Purchases model."""
        self.validate_item_has_units_registered_to_it()
        return super().clean()

    def save(self, *args, **kwargs):
        """Perform pre save and post save actions."""
        self.get_total_no_of_items()
        self.get_unit_price()
        super().save(*args, **kwargs)
        audit_fields = {
            'created_by': self.created_by,
            'updated_by': self.updated_by,
            'enterprise': self.enterprise,
        }

        if not WarehouseItem.objects.filter(item=self.item, enterprise=self.enterprise).exists():
            WarehouseItem.objects.create(
                item=self.item, **audit_fields)

        warehouse_item = WarehouseItem.objects.get(item=self.item, enterprise=self.enterprise)
        warehouse = Warehouse.objects.get(
            warehouse_type='PRIVATE', is_default=True, enterprise=self.enterprise, is_active=True)
        if not self.move_in_bulk:
            quantity_recorded = self.sale_units_purchased
        else:
            quantity_recorded = self.quantity_purchased

        WarehouseRecord.objects.create(
            warehouse=warehouse, warehouse_item=warehouse_item, record_type='ADD',
            quantity_recorded=quantity_recorded, unit_price=self.recommended_retail_price,
            **audit_fields)

        if self.quantity_to_inventory:
            WarehouseRecord.objects.create(
                warehouse=warehouse, warehouse_item=warehouse_item, record_type='REMOVE',
                quantity_recorded=self.quantity_to_inventory, removal_type='INVENTORY',
                removal_quantity_leaving_warehouse=self.quantity_to_inventory_on_display,
                removal_quantity_remaining_in_warehouse=self.quantity_to_inventory_in_warehouse,
                unit_price=self.recommended_retail_price, **audit_fields)
