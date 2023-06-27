"""Purchases models file."""

import decimal

from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator

from elites_retail_portal.common.models import AbstractBase
from elites_retail_portal.warehouses.models import (
    WarehouseItem, WarehouseRecord)
from elites_retail_portal.items.models import Item, ItemUnits
from elites_retail_portal.enterprises.models import Enterprise
from elites_retail_portal.debit import models as debit_models
from elites_retail_portal.enterprise_mgt.helpers import get_valid_enterprise_setup_rules
from elites_retail_portal.catalog.models import CatalogItem
from elites_retail_portal.procurement.models import PurchaseOrder


PAYMENT_METHOD_CHOICES = (
    ('PDQ', 'PDQ'),
    ('CASH', 'CASH'),
    ('CARD', 'CARD'),
    ('WALLET', 'WALLET'),
    ('MPESA TILL', 'MPESA TILL'),
    ('BANK CHEQUE', 'BANK CHEQUE'),
    ('MPESA PAYBILL', 'MPESA PAYBILL'),
    ('BANK WIRE TRANSFER', 'BANK WIRE TRANSFER'),
    ('BANK DIRECT DEPOSIT', 'BANK DIRECT DEPOSIT'),
)


class Purchase(AbstractBase):
    """Purchases model."""

    purchase_order = models.ForeignKey(
        PurchaseOrder, max_length=250, null=True, blank=True, on_delete=models.PROTECT)
    supplier = models.ForeignKey(
        Enterprise, max_length=250, null=False, blank=False,
        related_name='supplier_enterprise', on_delete=models.PROTECT)
    invoice_number = models.CharField(
        null=True, blank=True, max_length=300)
    purchase_date = models.DateTimeField(db_index=True, default=timezone.now)

    @property
    def total_cost(self):
        """Get the total cost."""
        items_costs = PurchaseItem.objects.filter(
            purchase=self).values_list('total_cost', flat=True)
        items_cost = sum(items_costs)
        returns_prices = debit_models.PurchasesReturn.objects.filter(
            purchase_item__purchase=self).values_list('total_cost', flat=True)
        returns_price = sum(returns_prices)

        return float(items_cost) - float(returns_price)

    @property
    def total_payments_amount(self):
        """Get total paid amount."""
        payment_amounts = PurchasePayment.objects.filter(
            purchase=self).values_list("amount", flat=True)
        return float(sum(payment_amounts))

    @property
    def balance_amount(self):
        """Get the total balance amount."""
        return float(self.total_cost) - float(self.total_payments_amount)

    def validate_unique_invoice_number_per_supplier(self):
        """Validate invoice number is unique for the given supplier."""
        if self.__class__.objects.filter(
                invoice_number=self.invoice_number, enterprise=self.enterprise,
                supplier=self.supplier).exclude(id=self.id).exists():
            msg = 'A purchase from {} for the invoice number {} already exists. '\
                'Please supply a new invoice number or update the existing record'.format(
                    self.supplier.name, self.invoice_number)
            raise ValidationError({'invoice_number': msg})

    def clean(self) -> None:
        """Clean the purchase model."""
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
    total_quantity_puchased = models.FloatField(null=True, blank=True)
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
    quantity_to_inventory = models.FloatField(null=True, blank=True, default=0)
    quantity_to_inventory_on_display = models.FloatField(null=True, blank=True, default=0)
    quantity_to_inventory_in_warehouse = models.FloatField(null=True, blank=True, default=0)
    move_in_bulk = models.BooleanField(default=False)
    added_to_warehouse = models.BooleanField(default=False)

    @property
    def item_units(self):
        """Get the item units."""
        return ItemUnits.objects.filter(item=self.item).first()

    @property
    def purchase_units(self):
        """Get the purchase units."""
        item_units = ItemUnits.objects.filter(item=self.item).first()
        return item_units.purchases_units

    @property
    def sale_units(self):
        """Get the sale units."""
        item_units = ItemUnits.objects.filter(item=self.item).first()
        return item_units.sales_units

    @property
    def unit_quantity_to_inventory(self):
        """Get the quantity of units to inventory."""
        return self.quantity_to_inventory * self.item_units.quantity_of_sale_units_per_purchase_unit    # noqa

    @property
    def unit_quantity_to_inventory_on_display(self):
        """Get the quantity of units on display."""
        return self.quantity_to_inventory_on_display * self.item_units.quantity_of_sale_units_per_purchase_unit # noqa

    def get_unit_cost(self):
        """Calculate buying price per unit."""
        total_no_of_items = self.sale_units_purchased
        buying_price = decimal.Decimal(
            float(self.total_cost) / total_no_of_items).quantize(
                decimal.Decimal('0.00'), rounding=decimal.ROUND_CEILING)

        self.unit_cost = buying_price

    def get_recommended_retail_price(self):
        """Get recommended retail price."""
        if not self.recommended_retail_price:
            catalog_item = CatalogItem.objects.filter(
                inventory_item__item=self.item, is_active=True).first()
            if catalog_item:
                self.recommended_retail_price = catalog_item.marked_price

    def get_total_no_of_items(self):
        """Get the total number selling units eg 12 packets from a dozen purchased."""
        item_units = ItemUnits.objects.filter(item=self.item).first()
        sale_units_per_purchase_unit = item_units.quantity_of_sale_units_per_purchase_unit
        total_no_of_items = sale_units_per_purchase_unit * self.quantity_purchased
        self.sale_units_purchased = total_no_of_items

    def validate_item_is_active(self):
        """Validate the item is active."""
        if not self.item.is_active:
            msg = "The item {} is not active. Please activate it to proceed".format(
                self.item.item_name)
            raise ValidationError({'item': msg})

    def validate_enterprise_has_setup_rules(self):
        """Validate that enterprise has set up rules."""
        rule = get_valid_enterprise_setup_rules(self.enterprise)
        # These are self checks which will raise validation errors if the values do not exist
        rule.default_inventory
        rule.default_catalog
        rule.default_warehouse
        rule.receiving_warehouse

    def validate_unique_item_per_purchase(self):
        """Validate that an item is unique for each purchase."""
        if self.__class__.objects.filter(
                purchase=self.purchase, item=self.item).exclude(id=self.id).exists():
            msg = 'The item {} already exists in this purchase instance. '\
                'Kindly select a new item or update the existing record'.format(
                    self.item.item_name)
            raise ValidationError({'item': msg})

    def validate_item_has_units_registered_to_it(self):
        """Validate that the items purchased have units to measure them."""
        from elites_retail_portal.items.models import ItemUnits
        if not ItemUnits.objects.filter(item=self.item).exists():
            raise ValidationError(
                {'item_units': 'Please register the units used to record this item'})

    def validate_quantity_moved_less_than_quantity_purchased(self):
        """Validate the quantity moved if less than the quantity purchased."""
        if self.unit_quantity_to_inventory > self.total_quantity_puchased:
            msg = 'You are trying to move {} {} of {} to inventory '\
                'which is more that the quantity purchased {} {}'.format(
                    self.quantity_to_inventory, self.purchase_units.units_name,
                    self.item.item_name, self.quantity_purchased,
                    self.purchase_units.units_name)
            raise ValidationError(
                {'quantity_to_inventory': msg})

        if self.unit_quantity_to_inventory_on_display > self.total_quantity_puchased:
            msg = 'You are trying to move {} {} of {} to display '\
                'which is more that the quantity purchased {} {}'.format(
                    self.quantity_to_inventory_on_display, self.purchase_units.units_name,
                    self.item.item_name, self.quantity_purchased, self.purchase_units.units_name)
            raise ValidationError(
                {'quantity_to_inventory_on_display': msg})

        if self.unit_quantity_to_inventory_on_display > self.unit_quantity_to_inventory:
            msg = 'The quantity to display {} {} '\
                'cannot be more than the quantity to inventory {} {}'.format(
                    self.quantity_to_inventory_on_display, self.purchase_units.units_name,
                    self.quantity_to_inventory, self.purchase_units.units_name)
            raise ValidationError(
                {'quantity_to_inventory_on_display': msg})

    def clean(self) -> None:
        """Clean the Purchases model."""
        self.validate_item_is_active()
        self.validate_enterprise_has_setup_rules()
        self.validate_quantity_moved_less_than_quantity_purchased()
        self.validate_unique_item_per_purchase()
        self.validate_item_has_units_registered_to_it()
        return super().clean()

    def save(self, *args, **kwargs):
        """Perform pre save and post save actions."""
        item_units = ItemUnits.objects.filter(item=self.item, is_active=True).first()
        if not item_units:
            msg = "The item {} does not have units assigned to it. "\
                "Please assign its respective units to proceed".format(self.item.item_name)
            raise ValidationError({'item': msg})
        sale_units_per_purchase_unit = item_units.quantity_of_sale_units_per_purchase_unit
        self.total_quantity_puchased = (
            item_units.quantity_of_sale_units_per_purchase_unit * self.quantity_purchased)
        self.quantity_to_inventory_in_warehouse = (
            float(self.quantity_to_inventory) - float(self.quantity_to_inventory_on_display))

        self.get_total_no_of_items()
        self.get_unit_cost()
        super().save(*args, **kwargs)

        if not self.added_to_warehouse:
            audit_fields = {
                'created_by': self.created_by,
                'updated_by': self.updated_by,
                'enterprise': self.enterprise,
            }

            if not WarehouseItem.objects.filter(
                    item=self.item, enterprise=self.enterprise).exists():
                WarehouseItem.objects.create(
                    item=self.item, **audit_fields)

            warehouse_item = WarehouseItem.objects.get(
                item=self.item, enterprise=self.enterprise)
            rule = get_valid_enterprise_setup_rules(self.enterprise)
            receiving_warehouse = rule.receiving_warehouse

            warehouse_record = WarehouseRecord.objects.filter(addition_guid=self.id).first()
            if warehouse_record:
                warehouse_record.warehouse = receiving_warehouse
                warehouse_record.warehouse_item = warehouse_item
                warehouse_record.quantity_recorded = self.sale_units_purchased
                warehouse_record.unit_price = self.recommended_retail_price
                warehouse_record.save()
            else:
                warehouse_record = WarehouseRecord.objects.create(
                    warehouse=receiving_warehouse, warehouse_item=warehouse_item,
                    record_type='ADD', addition_guid=self.id,
                    quantity_recorded=self.sale_units_purchased,
                    unit_price=self.recommended_retail_price, **audit_fields)

            if rule.receiving_warehouse == rule.default_warehouse:
                warehouse_record = WarehouseRecord.objects.filter(
                    record_type='REMOVE', addition_guid=self.id).first()
                quantity_recorded = (
                    sale_units_per_purchase_unit * self.quantity_to_inventory
                    ) if self.quantity_to_inventory else 0
                if warehouse_record:
                    warehouse_record.warehouse = receiving_warehouse
                    warehouse_record.warehouse_item = warehouse_item
                    warehouse_record.quantity_recorded = quantity_recorded
                    warehouse_record.unit_price = self.recommended_retail_price
                    warehouse_record.removal_quantity_leaving_warehouse = self.quantity_to_inventory_on_display # noqa
                    warehouse_record.removal_quantity_remaining_in_warehouse = self.quantity_to_inventory_in_warehouse  # noqa
                    warehouse_record.updated_by = self.updated_by
                    warehouse_record.save()

                else:
                    if self.quantity_to_inventory:
                        WarehouseRecord.objects.create(
                            warehouse=receiving_warehouse, warehouse_item=warehouse_item,
                            record_type='REMOVE', quantity_recorded=quantity_recorded,
                            removal_type='INVENTORY', addition_guid=self.id,
                            removal_quantity_leaving_warehouse=self.quantity_to_inventory_on_display,   # noqa
                            removal_quantity_remaining_in_warehouse=self.quantity_to_inventory_in_warehouse,    # noqa
                            unit_price=self.recommended_retail_price, **audit_fields)

                self.added_to_warehouse = True
                self.save()


class PurchasePayment(AbstractBase):
    """Purchase Payment model."""

    payment_time = models.DateTimeField(db_index=True, default=timezone.now)
    purchase = models.ForeignKey(
        Purchase, max_length=250, null=False, blank=False,
        related_name='invoice_payment', on_delete=models.PROTECT)
    payment_method = models.CharField(max_length=300, choices=PAYMENT_METHOD_CHOICES)
    amount = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=False, blank=False)
    note = models.TextField(null=True, blank=True)
