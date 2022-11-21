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
from elites_franchise_portal.debit import models as debit_models
from elites_franchise_portal.enterprise_mgt.helpers import get_valid_enterprise_setup_rules

class Purchase(AbstractBase):
    """Purchases model."""

    supplier = models.ForeignKey(
        Enterprise, max_length=250, null=False, blank=False,
        related_name='supplier_enterprise', on_delete=models.PROTECT)
    invoice_number = models.CharField(
        null=True, blank=True, max_length=300)
    purchase_date = models.DateTimeField(db_index=True, default=timezone.now)

    @property
    def total_cost(self):
        items_costs = PurchaseItem.objects.filter(purchase=self).values_list('total_cost', flat=True)
        items_cost = sum(items_costs)
        returns_prices = debit_models.PurchasesReturn.objects.filter(purchase_item__purchase=self).values_list('total_price', flat=True)
        returns_price = sum(returns_prices)

        return float(items_cost) - float(returns_price)

    def validate_unique_invoice_number_per_supplier(self):
        if self.__class__.objects.filter(
                invoice_number=self.invoice_number, enterprise=self.enterprise,
                supplier=self.supplier).exclude(id=self.id).exists():
            msg = 'A purchase from {} for the invoice number {} already exists. '\
                'Kindly enter a new invoice number or update the existing record'.format(self.supplier.name, self.invoice_number)
            raise ValidationError({'invoice_number': msg})

    def clean(self) -> None:
        self.validate_unique_invoice_number_per_supplier()
        return super().clean()

class PurchaseItem(AbstractBase):
    """Purchase Item model."""

    purchase = models.ForeignKey(
        Purchase, max_length=250, null=False, blank=False,
        related_name='invoice_purchase', on_delete=models.PROTECT)
    item = models.ForeignKey(
        Item, null=False, blank=False, on_delete=models.PROTECT)
    quantity_purchased = models.FloatField(null=False, blank=False)
    sale_units_purchased = models.FloatField(null=True, blank=True)
    unit_cost = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=True, blank=True, default=0.0)
    total_cost = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=False, blank=False)
    recommended_retail_price = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=True, blank=True, default=0.0)
    quantity_to_inventory = models.FloatField(null=True, blank=True)
    quantity_to_inventory_on_display = models.FloatField(null=True, blank=True)
    quantity_to_inventory_in_warehouse = models.FloatField(null=True, blank=True)
    move_in_bulk = models.BooleanField(default=False)
    added_to_warehouse = models.BooleanField(default=False)

    def get_unit_cost(self):
        """Calculate buying price per unit."""
        total_no_of_items = self.sale_units_purchased
        buying_price = decimal.Decimal(
            float(self.total_cost) / total_no_of_items).quantize(
                decimal.Decimal('0.00'), rounding=decimal.ROUND_CEILING)

        self.unit_cost = buying_price

    def get_total_no_of_items(self):
        """Get the total number selling units eg 12 packets from a dozen purchased."""
        if not self.sale_units_purchased:
            item_units = ItemUnits.objects.filter(item=self.item).first()
            sale_units_per_purchase_unit = item_units.quantity_of_sale_units_per_purchase_unit
            total_no_of_items = sale_units_per_purchase_unit * self.quantity_purchased
            self.sale_units_purchased = total_no_of_items

    def validate_enterprise_has_setup_rules(self):
        rule = get_valid_enterprise_setup_rules(self.enterprise)
        # These are self checks which will raise validation errors if the values do not exist
        rule.default_inventory
        rule.default_catalog
        rule.default_warehouse
        rule.receiving_warehouse

    def validate_unique_item_per_purchase(self):
        if self.__class__.objects.filter(purchase=self.purchase, item=self.item).exclude(id=self.id).exists():
            msg = 'The item {} already exists in this purchase instance. '\
                'Kindly select a new item or update the existing record'.format(self.item.item_name)
            raise ValidationError({'item': msg})

    def validate_item_has_units_registered_to_it(self):
        """Validate that the items purchased have units to measure them."""
        from elites_franchise_portal.items.models import ItemUnits
        if not ItemUnits.objects.filter(item=self.item).exists():
            raise ValidationError(
                {'item_units': 'Please register the units used to record this item'})

    def validate_quantity_to_inventory_less_than_quantity_purchased(self):
        if self.quantity_to_inventory > self.quantity_purchased:
            msg = '{} items to inventory cannot be more that the quantity purchased {}'.format(
                self.quantity_to_inventory, self.quantity_purchased)
            raise ValidationError(
                {'quantity_to_inventory': msg})

        if self.quantity_to_inventory_on_display > self.quantity_purchased:
            msg = '{} items to display cannot be more that the quantity purchased {}'.format(
                self.quantity_to_inventory_on_display, self.quantity_purchased)
            raise ValidationError(
                {'quantity_to_inventory_on_display': msg})

    def clean(self) -> None:
        """Clean the Purchases model."""
        self.validate_enterprise_has_setup_rules()
        self.validate_quantity_to_inventory_less_than_quantity_purchased()
        self.validate_unique_item_per_purchase()
        self.validate_item_has_units_registered_to_it()
        return super().clean()

    def save(self, *args, **kwargs):
        """Perform pre save and post save actions."""
        self.get_total_no_of_items()
        self.get_unit_cost()
        super().save(*args, **kwargs)
        if not self.added_to_warehouse:
            audit_fields = {
                'created_by': self.created_by,
                'updated_by': self.updated_by,
                'enterprise': self.enterprise,
            }

            if not WarehouseItem.objects.filter(item=self.item, enterprise=self.enterprise).exists():
                WarehouseItem.objects.create(
                    item=self.item, **audit_fields)

            warehouse_item = WarehouseItem.objects.get(item=self.item, enterprise=self.enterprise)
            rule = get_valid_enterprise_setup_rules(self.enterprise)
            receiving_warehouse = rule.receiving_warehouse

            if not self.move_in_bulk:
                quantity_recorded = self.sale_units_purchased
            else:
                quantity_recorded = self.quantity_purchased

            WarehouseRecord.objects.create(
                warehouse=receiving_warehouse, warehouse_item=warehouse_item, record_type='ADD',
                quantity_recorded=quantity_recorded, unit_price=self.recommended_retail_price,
                **audit_fields)

            if self.quantity_to_inventory:
                if rule.receiving_warehouse == rule.default_warehouse:
                    WarehouseRecord.objects.create(
                        warehouse=receiving_warehouse, warehouse_item=warehouse_item, record_type='REMOVE',
                        quantity_recorded=self.quantity_to_inventory, removal_type='INVENTORY',
                        removal_quantity_leaving_warehouse=self.quantity_to_inventory_on_display,
                        removal_quantity_remaining_in_warehouse=self.quantity_to_inventory_in_warehouse,
                        unit_price=self.recommended_retail_price, **audit_fields)

                    self.added_to_warehouse = True
                    self.save()
                else:
                    # TODO Add record to the default warehouse then move them to the default inventory form the default warehouse
                    pass
