"""Inventory models file."""

from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

from elites_retail_portal.items.models import Item
from elites_retail_portal.common.models import AbstractBase

REMOVE_FROM_INVENTORY_CHOICES = (
    ('SALES', 'SALES'),
    ('DAMAGES', 'DAMAGES'),
    ('SAFETY STOCK', 'SAFETY STOCK'),
    ('SALES RETURNS', 'SALES RETURNS'),
    ('PURCHASES RETURNS', 'PURCHASES RETURNS'),
)

RECORD_TYPE_CHOICES = (
    ('ADD', 'ADD'),
    ('REMOVE', 'REMOVE'),
)

AUDIT_CREATE_OPERATION_CHOICES = ['CREATE CATALOG ITEM', 'CREATE INVENTORY RECORD']

INVENTORY_TYPE_CHOICES = (
    ('EXCESS', 'EXCESS'),
    ('SERVICE', 'SERVICE'),
    ('AVAILABLE', 'AVAILABLE'),
    ('ALLOCATED', 'ALLOCATED'),
    ('DECOUPLING', 'DECOUPLING'),
    ('THEORETICAL', 'THEORETICAL'),
    ('SAFETY STOCK', 'SAFETY STOCK'),
    ('WORKING STOCK', 'WORKING STOCK'),
    ('PSYCHIC STOCK', 'PSYCHIC STOCK'),
    ('RAW MATERIALS', 'RAW MATERIALS'),
    ('FINISHED GOODS', 'FINISHED GOODS'),
    ('WORK IN PROCESS', 'WORK IN PROCESS'),
    ('IN TRANSIT STOCK', 'IN TRANSIT STOCK'),
    ('PACKING MATERIALS', 'PACKING MATERIALS'),
    ('ANTICIPATORY STOCK', 'ANTICIPATORY STOCK'),
    ('MAINTENANCE, REPAIR AND OPERATING', 'MAINTENANCE, REPAIR AND OPERATING'),
)

SALES = 'SALES'
ADD = 'ADD'
REMOVE = 'REMOVE'
INVENTORY = 'INVENTORY'
AVAILABLE = 'AVAILABLE'
ALLOCATED = 'ALLOCATED'
WORKING_STOCK = 'WORKING STOCK'


class InventoryItem(AbstractBase):
    """Inventory item model."""

    item = models.OneToOneField(
        Item, null=False, blank=False, unique=True, on_delete=models.PROTECT)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    @property
    def summary(self):
        """Get summary of item's summary."""
        records = InventoryRecord.objects.filter(inventory_item=self)
        available_quantity = 0
        if records.exists():
            for record in records:
                if record.closing_stock_quantity >= available_quantity:
                    available_quantity = record.closing_stock_quantity

        summary = {
            'available_quantity': available_quantity,
            'total': '',
        }
        return summary

    @property
    def quantity(self):
        """Get total quantity of item in inventory."""
        records = InventoryRecord.objects.filter(inventory_item=self)
        if records:
            record = records.latest('record_date')
            return record.closing_stock_quantity
        return 0

    @property
    def total_amount(self):
        """Get the total amount of item in inventory."""
        records = InventoryRecord.objects.filter(inventory_item=self)
        if records:
            record = records.latest('record_date')
            return record.closing_stock_total_amount
        return 0

    @property
    def unit_price(self):
        """Get the unit price."""
        records = InventoryRecord.objects.filter(
            inventory_item=self, record_type='ADD')
        if records:
            record = records.latest('record_date')
            return record.unit_price
        return 0

    def check_item_in_warehouse(self):
        """Check item exists in store."""
        from .import WarehouseItem
        warehouse_item_exists = WarehouseItem.objects.filter(item=self.item).exists()
        if not warehouse_item_exists:
            data = {
                'updated_by': self.updated_by,
                'created_by': self.created_by,
                'item': self.item,
                'enterprise': self.enterprise,
            }
            WarehouseItem.objects.create(**data)

    def check_inventory_item_in_catalog_items(self, section):
        """Check that item exists in catalog items."""
        from elites_retail_portal.catalog.models import CatalogItem
        data = {
            'updated_by': self.updated_by,
            'created_by': self.created_by,
            'enterprise': self.enterprise,
            'marked_price': self.unit_price,
            'selling_price': self.unit_price,
            'quantity': self.summary['available_quantity'],
            'section': section,
            }
        defaults = {
            'inventory_item': self,
            'enterprise': self.enterprise,
            }
        CatalogItem.objects.update_or_create(defaults=defaults, **data)

    def __str__(self):
        """Str representation for the inventory_item."""
        return '{}'.format(self.item.item_name)

    def save(self, *args, **kwargs):
        """Super save to perform pre and post save."""
        super().save(*args, **kwargs)
        inventory = Inventory.objects.filter(
            is_master=True, is_active=True, enterprise=self.enterprise)
        inventory = inventory.first()
        if inventory:
            audit_fields = {
                'updated_by': self.updated_by,
                'created_by': self.created_by,
                'enterprise': self.enterprise
                }

            InventoryInventoryItem.objects.filter(
                inventory=inventory, inventory_item=self, **audit_fields)

    class Meta:
        """Meta class for inventory model."""

        ordering = ['item__item_name']


class Inventory(AbstractBase):
    """Inventory model."""

    inventory_name = models.CharField(max_length=300)
    inventory_code = models.CharField(max_length=300, null=True, blank=True)
    inventory_type = models.CharField(
        max_length=300, choices=INVENTORY_TYPE_CHOICES, default=WORKING_STOCK)
    inventory_items = models.ManyToManyField(
        InventoryItem, through='InventoryInventoryItem', related_name='inventoryinventoryitems')
    description = models.TextField(null=True, blank=True)
    is_master = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    pushed_to_edi = models.BooleanField(default=False)

    @property
    def summary(self):
        """Summary."""
        inventory_items = self.inventory_items.filter(is_active=True)
        inventory_records = InventoryRecord.objects.filter(
            inventory=self, inventory_item__in=inventory_items, enterprise=self.enterprise)

        summary = []
        if inventory_records.exists():
            for inventory_item in inventory_items:
                try:
                    latest_inventory_item_record = inventory_records.filter(
                        inventory_item=inventory_item).latest('record_date')
                    quantity = latest_inventory_item_record.closing_stock_quantity
                    total_amount = latest_inventory_item_record.closing_stock_total_amount
                    data = {
                        'inventory_item': inventory_item,
                        'quantity': quantity,
                        'total_amount': total_amount,
                        }
                    summary.append(data)
                except Exception:
                    pass

        return summary

    def get_inventory_item_summary(self, inventory_item):
        """Get inventory item summary."""
        records = InventoryRecord.objects.filter(
            inventory=self, inventory_item=inventory_item)

        summary = {
            'opening_stock_quantity': 0,
            'opening_stock_total_amount': 0,
            'quantity_recorded': 0,
            'total_amount_recorded': 0,
            'closing_stock_quantity': 0,
            'closing_stock_total_amount': 0,
        }

        if not records.exists():
            return summary

        latest_record = records.latest('record_date')
        summary['opening_stock_quantity'] = latest_record.opening_stock_quantity
        summary['opening_stock_total_amount'] = latest_record.opening_stock_total_amount
        summary['quantity_recorded'] = latest_record.quantity_recorded
        summary['total_amount_recorded'] = latest_record.total_amount_recorded
        summary['closing_stock_quantity'] = latest_record.closing_stock_quantity
        summary['closing_stock_total_amount'] = latest_record.closing_stock_total_amount

        return summary

    def validate_unique_active_master_inventory_for_enterprise(self):
        """Validate unique active master inventory for the enterprise."""
        if self.is_master:
            master_inventory = self.__class__.objects.filter(
                is_active=True, is_master=True, enterprise=self.enterprise).exclude(id=self.id)
            if master_inventory.exists():
                msg = 'You can only have one active master inventory'
                raise ValidationError({'inventory': msg})

    def validate_unique_active_inventory_per_type_for_enterprise(self):
        """Validate unique active inventory per enterprise."""
        inventory = self.__class__.objects.filter(
            inventory_type=self.inventory_type, is_active=True,
            enterprise=self.enterprise).exclude(id=self.id)
        if inventory.exists():
            msg = 'You can only have one active {} inventory'.format(self.inventory_type.title())
            raise ValidationError({'inventory': msg})

    def validate_unique_default_inventory_per_enterprise(self):
        """Validate unique default inventory per enterprise."""
        if self.is_default and self.__class__.objects.filter(
                is_active=True, is_default=True,
                enterprise=self.enterprise).exclude(id=self.id).exists():
            msg = "You can only have one active default inventory"
            raise ValidationError({'default_inventory': msg})

    def clean(self) -> None:
        """Clean inventory."""
        self.validate_unique_default_inventory_per_enterprise()
        self.validate_unique_active_master_inventory_for_enterprise()
        self.validate_unique_active_inventory_per_type_for_enterprise()
        return super().clean()


class InventoryInventoryItem(AbstractBase):
    """Inventory Invetory Item model."""

    inventory = models.ForeignKey(Inventory, on_delete=models.PROTECT)
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)
    pushed_to_edi = models.BooleanField(default=False)


class InventoryRecord(AbstractBase):
    """Inventory Record class."""

    record_date = models.DateTimeField(db_index=True, default=timezone.now)
    inventory = models.ForeignKey(Inventory, on_delete=models.PROTECT)
    inventory_item = models.ForeignKey(
        InventoryItem, null=False, blank=False, on_delete=models.PROTECT)
    record_code = models.CharField(max_length=300, null=True, blank=True)
    opening_stock_quantity = models.FloatField(null=True, blank=True, default=0)
    opening_stock_total_amount = models.FloatField(null=True, blank=True, default=0)
    record_type = models.CharField(max_length=300, choices=RECORD_TYPE_CHOICES, default=ADD)
    quantity_recorded = models.FloatField(null=False, blank=False)
    unit_price = models.FloatField(null=False, blank=False)
    total_amount_recorded = models.FloatField(null=True, blank=True)
    removal_type = models.CharField(
        max_length=300, null=True, blank=True, choices=REMOVE_FROM_INVENTORY_CHOICES)
    removal_guid = models.UUIDField(null=True, blank=True)
    addition_guid = models.UUIDField(null=True, blank=True)
    closing_stock_quantity = models.FloatField(null=True, blank=True, default=0)
    closing_stock_total_amount = models.FloatField(null=True, blank=True, default=0)
    quantity_of_stock_on_display = models.FloatField(null=True, blank=True)
    quantity_of_stock_in_warehouse = models.FloatField(null=True, blank=True)
    quantity_of_stock_on_sale = models.FloatField(null=True, blank=True)
    quantity_sold = models.FloatField(null=True, blank=True)
    remaining_stock_total_amount = models.FloatField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    updated_catalog = models.BooleanField(default=False)

    # TODO Refactor to use recommended retail price for updating the selling prices of items

    @property
    def source(self):
        """Get record source."""
        from elites_retail_portal.debit.models import SaleItem
        if self.record_type == "ADD" and SaleItem.objects.filter(id=self.addition_guid).exists():
            return "RECEIPT CANCELATION"

        return None

    def get_latest_record(self, record_type=None):
        """Get the latest record."""
        record = None
        record_type = record_type if record_type else self.record_type
        records = self.__class__.objects.filter(
            inventory=self.inventory, inventory_item=self.inventory_item, record_type=record_type,
            enterprise=self.enterprise)
        if records:
            record = records.latest('record_date')

        return record

    def validate_inventory_item_exists_in_inventory(self):
        """Validate inventory item exists in inventory."""
        if not InventoryInventoryItem.objects.filter(
                inventory=self.inventory, inventory_item=self.inventory_item,
                is_active=True).exists():
            inventory_item = self.inventory_item.item.item_name
            inventory_type = self.inventory.inventory_type.title()
            raise ValidationError(
                {'inventory_item': '{} is not hooked up to an active {} Inventory. '
                 'Please set that up first'.format(inventory_item, inventory_type)})

    def validate_unique_addition_guid(self):
        """Validate a record is created once from the given source."""
        if self.addition_guid and self.__class__.objects.filter(
                addition_guid=self.addition_guid).exclude(id=self.id).exists():
            msg = "An inventory record from this source already exists, please audit your entries"
            raise ValidationError({"addition": msg})

    def get_opening_stock(self):
        """Initialize opening stock."""
        existing_record = self.__class__.objects.filter(id=self.id).first()
        records = self.__class__.objects.filter(
            inventory=self.inventory, inventory_item=self.inventory_item,
            record_date__lte=self.record_date).exclude(id=self.id)

        if records.exists():
            if existing_record:
                self.opening_stock_quantity = existing_record.opening_stock_quantity
            latest_record = records.latest('record_date')
            self.opening_stock_quantity = latest_record.closing_stock_quantity
            self.opening_stock_total_amount = latest_record.closing_stock_total_amount
        else:
            self.opening_stock_quantity = 0.0
            self.opening_stock_total_amount = 0.0

    def calculate_total_amount_recorded(self):
        """Calculate total amount recorded."""
        self.total_amount_recorded = round(
            Decimal(float(self.quantity_recorded) * float(self.unit_price)), 2)

    def calculate_closing_stock_quantity(self):
        """Calculate quantity of closing stock."""
        record = self.__class__.objects.filter(id=self.id).first()
        if record:
            # It is an update
            # Ensure accuracy in opening_stock_quantity
            if self.record_type == ADD:
                self.closing_stock_quantity = self.opening_stock_quantity + self.quantity_recorded

            if self.record_type == REMOVE:
                self.closing_stock_quantity = self.opening_stock_quantity - self.quantity_recorded

        else:
            if self.record_type == ADD:
                recorded_quantity = self.quantity_recorded
                recorded_total_amount = self.total_amount_recorded

            if self.record_type == REMOVE:
                recorded_quantity = -(self.quantity_recorded)
                latest_add = self.get_latest_record('ADD')
                unit_price = latest_add.unit_price if latest_add else self.unit_price
                recorded_total_amount = -(float(unit_price) * self.quantity_recorded)

            self.closing_stock_quantity = self.opening_stock_quantity + recorded_quantity
            self.closing_stock_total_amount = round(
                Decimal(float(self.opening_stock_total_amount) + float(recorded_total_amount)), 2)

    def validate_enterprise_has_set_up_rules(self):
        """Validate the enterprise has set up rules."""
        from elites_retail_portal.enterprise_mgt.helpers import (
            get_valid_enterprise_setup_rules)
        enterprise_setup_rules = get_valid_enterprise_setup_rules(self.enterprise)
        if not enterprise_setup_rules:
            msg = 'You do not have rules for your enterprise. Please set that up first'
            raise ValidationError({'enterprise_setup_rules': msg})

    def validate_quantity_of_stock_in_warehouse(self):
        """Validate quantity of stock in store."""
        from .import Store
        if self.quantity_of_stock_in_warehouse:
            try:
                store_item = Store.objects.get(item=self.item)
            except Store.DoesNotExist:
                raise ValidationError(
                    {'item': 'The item does not a record in the store'})

            if self.quantity_of_stock_in_warehouse > store_item.closing_quantity:
                raise ValidationError(
                    {'quantity in store': 'Quantity in store is less than the added quantity'})

    def validate_quantity_of_stock_on_sale(self):
        """Validate quantity on stock matches expected quantity on stock."""
        expected_stock_on_sale = sum(
            [self.quantity_of_stock_on_display, self.quantity_of_stock_in_warehouse])
        if not self.quantity_of_stock_on_sale == expected_stock_on_sale:
            raise ValidationError(
                {'quantiy on sale': 'Quantity of stock on sale does not match the expected quantity.'}) # noqa

    def validate_quantity_sold(self):
        """Validate quantity sold matches expected quantity sold."""
        expected_no_of_sold_items = self.__class__.objects.filter(
            item=self.inventory_item, removal_type=SALES).count()

        if not self.quantity_sold == expected_no_of_sold_items:
            raise ValidationError(
                {'quantity sold': 'The quantity sold does not match the expected quantity sold'})

    def validate_cannot_remove_more_than_existing_items(self):
        """Validate removal quantity not more than available quantity."""
        from elites_retail_portal.catalog.models import CatalogItem
        catalog_item = CatalogItem.objects.filter(inventory_item=self.inventory_item).first()
        if catalog_item:
            if self.record_type == REMOVE and self.quantity_recorded > catalog_item.quantity:
                raise ValidationError(
                    {'quantity': 'You are trying to remove {} items of '
                        '{} and {} has {} items'.format(
                            self.quantity_recorded, self.inventory_item.item.item_name,
                            self.inventory.inventory_name, catalog_item.quantity)})

    def validate_removal_from_inventory(self):
        """Validate removal item has removal type."""
        if self.record_type == REMOVE:
            if not self.removal_type:
                msg = 'Please specify where to the items are being taken to from the inventory'
                raise ValidationError(
                    {'removal type': msg})

            if not self.removal_guid:
                msg = 'Please specify the id of where to the items are being taken'\
                    'from the inventory'
                raise ValidationError({'removal_guid': msg})

    def validate_unique_record_code(self):
        """Validate record code is unique for the inventory."""
        record = self.__class__.objects.filter(
            inventory=self.inventory, record_code=self.record_code)
        if record.exclude(id=self.id).exists():
            raise ValidationError(
                {'record_code': 'A record with this record code already exists. '
                    'Please supply a unique record code'})

    def clean(self) -> None:
        """Clean Inventory Record."""
        # TODO Switch operation type to audit_type
        self.validate_enterprise_has_set_up_rules()
        self.validate_inventory_item_exists_in_inventory()
        self.validate_unique_addition_guid()
        self.validate_cannot_remove_more_than_existing_items()
        self.validate_removal_from_inventory()
        self.validate_unique_record_code()
        super().clean()

    def update_catalog_item(self):
        """Update Catalog item."""
        from elites_retail_portal.enterprise_mgt.helpers import (
            get_valid_enterprise_setup_rules)
        from elites_retail_portal.catalog.models import (
            CatalogItemAuditLog, CatalogCatalogItem, CatalogItem)

        enterprise_setup_rules = get_valid_enterprise_setup_rules(self.enterprise)
        available_inventory = enterprise_setup_rules.available_inventory
        standard_catalog = enterprise_setup_rules.standard_catalog
        audit_fields = {
            'created_by': self.created_by,
            'updated_by': self.updated_by,
            'enterprise': self.enterprise,
        }

        if not self.inventory.inventory_type == available_inventory.inventory_type:
            self.__class__.objects.filter(id=self.id).update(updated_catalog=False)
            return

        catalog_items = standard_catalog.catalog_items.filter(
            inventory_item=self.inventory_item, is_active=True, enterprise=self.enterprise)

        catalog_item = catalog_items.first()
        if not catalog_item:
            catalog_item = CatalogItem.objects.filter(
                inventory_item=self.inventory_item, is_active=True,
                enterprise=self.enterprise).first()
            if not catalog_item:
                self.__class__.objects.filter(id=self.id).update(updated_catalog=False)
                # The inventory item is not hooked as a catalog item
                return

            CatalogCatalogItem.objects.create(
                catalog=standard_catalog, catalog_item=catalog_item, **audit_fields)

        details_payload = {
            'quantity_before': catalog_item.quantity or 0,
            'quantity_recorded': self.quantity_recorded if self.record_type == ADD else -self.quantity_recorded,    # noqa
        }

        # Save to get the quantity
        if self.record_type == "ADD" and self.unit_price != catalog_item.marked_price:
            catalog_item.marked_price = self.unit_price

        catalog_item.quantity = catalog_item.get_quantity()
        catalog_item.save()
        catalog_item.refresh_from_db()

        catalog_item_audit_payload = {
            'catalog_item': catalog_item,
            'inventory_record': self,
            'operation_type': 'CREATE INVENTORY RECORD',
            'audit_type': 'CREATE',
            'record_type': self.record_type,
        }

        catalog_item_audit_logs = CatalogItemAuditLog.objects.filter(catalog_item=catalog_item)
        create_catalog_item_audit_logs = catalog_item_audit_logs.filter(
            audit_type='CREATE', operation_type__in=AUDIT_CREATE_OPERATION_CHOICES)
        if catalog_item_audit_logs.exists():
            latest_catalog_item_audit_log = catalog_item_audit_logs.latest('audit_date')
            details_payload[
                'marked_price_before'] = latest_catalog_item_audit_log.marked_price_after
            details_payload[
                'discount_amount_before'] = latest_catalog_item_audit_log.discount_amount_after
            details_payload[
                'selling_price_before'] = latest_catalog_item_audit_log.selling_price_after
            details_payload[
                'threshold_price_before'] = latest_catalog_item_audit_log.threshold_price_after

        if self.record_type == ADD:
            details_payload['marked_price_recorded'] = self.unit_price
            catalog_item_audit_payload['operation_type'] = 'UPDATE INVENTORY RECORD'
            record_catalog_item_audit_logs = catalog_item_audit_logs.filter(inventory_record=self)
            if not record_catalog_item_audit_logs.exists():
                audit_quantity = self.quantity_recorded
                if self.record_date < catalog_item.created_on:
                    catalog_item_audit_payload['audit_type'] = 'UPDATE'
                    latest_create_log = create_catalog_item_audit_logs.latest('audit_date')
                    audit_quantity = self.quantity_recorded - latest_create_log.quantity_recorded

                catalog_item.marked_price = self.unit_price
                catalog_item.save()

                details_payload['quantity_recorded'] = audit_quantity
                catalog_item_audit_payload['operation_type'] = 'CREATE INVENTORY RECORD'
                catalog_item_audit_payload['audit_type'] = 'CREATE'

                CatalogItemAuditLog.objects.create(
                    **catalog_item_audit_payload, **details_payload, **audit_fields)
                self.__class__.objects.filter(id=self.id).update(updated_catalog=True)
                return

            latest_record_catalog_item_audit_log = record_catalog_item_audit_logs.latest(
                'audit_date')
            create_record_catalog_item_audit_logs = record_catalog_item_audit_logs.filter(
                audit_type='CREATE', operation_type__in=AUDIT_CREATE_OPERATION_CHOICES)

            if latest_record_catalog_item_audit_log.quantity_recorded == self.quantity_recorded and latest_record_catalog_item_audit_log.marked_price_recorded == self.unit_price:  # noqa
                # Early return Quantities and Prices look good
                return

            if create_record_catalog_item_audit_logs.exists():
                audit_quantity = self.quantity_recorded
                latest_create_record_catalog_item_audit_log = create_record_catalog_item_audit_logs.latest('audit_date')    # noqa
                audit_quantity = self.quantity_recorded - latest_create_record_catalog_item_audit_log.quantity_recorded # noqa
                if self.record_date < catalog_item.created_on:
                    audit_quantity = self.quantity_recorded - latest_create_record_catalog_item_audit_log.quantity_after    # noqa
            else:
                latest_record_catalog_item_audit_log = record_catalog_item_audit_logs.latest(
                    'audit_date')
                audit_quantity = self.quantity_recorded - latest_record_catalog_item_audit_log.quantity_after   # noqa

            catalog_item.marked_price = self.unit_price
            details_payload['quantity_recorded'] = audit_quantity
            details_payload['quantity_recorded'] = audit_quantity
            catalog_item_audit_payload['audit_type'] = 'UPDATE'
            catalog_item_audit_payload['operation_type'] = 'UPDATE INVENTORY RECORD'
            CatalogItemAuditLog.objects.create(
                **catalog_item_audit_payload, **details_payload, **audit_fields)
            self.__class__.objects.filter(id=self.id).update(updated_catalog=True)
            return

        if self.record_type == REMOVE:
            catalog_item.refresh_from_db()
            details_payload['quantity_recorded'] = -self.quantity_recorded

            record_catalog_item_audit_logs = catalog_item_audit_logs.filter(inventory_record=self)
            if not record_catalog_item_audit_logs.exists():
                latest_catalog_item_audit_log = catalog_item_audit_logs.latest('audit_date')
                CatalogItemAuditLog.objects.create(
                    **catalog_item_audit_payload, **details_payload, **audit_fields)
                self.__class__.objects.filter(id=self.id).update(updated_catalog=True)
                return

            latest_record_catalog_item_audit_log = record_catalog_item_audit_logs.latest(
                'audit_date')

            if latest_record_catalog_item_audit_log.quantity_recorded == -self.quantity_recorded:  # noqa
                # Early return quantities look good
                return

            quantity_diff = self.quantity_recorded - abs(
                latest_record_catalog_item_audit_log.quantity_recorded)
            details_payload['quantity_recorded'] = -quantity_diff
            CatalogItemAuditLog.objects.create(
                **catalog_item_audit_payload, **details_payload, **audit_fields)
            self.__class__.objects.filter(id=self.id).update(updated_catalog=True)
            return

    def save(self, *args, **kwargs):
        """Perform pre save and post save actions on Catalog Item."""
        if not self.record_code:
            from random import randint
            self.record_code = str(randint(10000, 10000000))
        record = self.__class__.objects.filter(id=self.id).first()
        if record:
            self.record_date = record.record_date if record.record_date else timezone.now()
        self.get_opening_stock()
        self.calculate_total_amount_recorded()
        self.calculate_closing_stock_quantity()
        super().save(*args, **kwargs)
        self.update_catalog_item()
        existing_record = self.__class__.objects.filter(id=self.id).first()
        if existing_record:
            for record in InventoryRecord.objects.filter(
                    inventory=self.inventory, inventory_item=self.inventory_item,
                    record_date__gt=self.record_date):
                # NOTE If you remove the record date check it will loop infinitely
                record.save()

    class Meta:
        """Meta class for Base Inventory class."""

        ordering = ['inventory_item__item__item_name']


def get_latest_inventory_record(inventory, inventory_item):
    """Get the latest inventory record."""
    InventoryRecord.objects.filter(
        inventory=inventory, inventory_item=inventory_item).latest('record_date')
