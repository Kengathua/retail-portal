"""Store models file."""

from django.db import models
from django.utils import timezone
from django.db.models import PROTECT
from django.core.exceptions import ValidationError

from elites_retail_portal.items.models import Item
from elites_retail_portal.common.models import AbstractBase
from elites_retail_portal.debit.models import (
    InventoryItem, InventoryInventoryItem, InventoryRecord)

REMOVE_FROM_STOCK_CHOICES = (
    ('SALES', 'SALES'),
    ('DAMAGES', 'DAMAGES'),
)

REMOVE_FROM_WAREHOUSE_CHOICES = (
    ('INVENTORY', 'INVENTORY'),
    ('DAMAGES', 'DAMAGES'),
    ('SUPPLIES', 'SUPPLIES'),
)

RECORD_TYPE_CHOICES = (
    ('ADD', 'ADD'),
    ('REMOVE', 'REMOVE'),
    ('TRANSFER', 'TRANSFER')
)

WAREHOUSE_TYPE_CHOICES = (
    ('PUBLIC', 'PUBLIC'),
    ('PRIVATE', 'PRIVATE'),
    ('BONDED', 'BONDED'),
    ('SMART', 'SMART'),
    ('CONSOLIDATED', 'CONSOLIDATED'),
    ('COOPERATIVE', 'COOPERATIVE'),
    ('GOVERNMENT', 'GOVERNMENT'),
    ('DISTRIBUTION CENTER', 'DISTRIBUTION CENTER')
)

WAREHOUSE_PROCESS_CHOICES = (
    ('RECEIVING', 'RECEIVING'),
    ('PUT AWAY', 'PUT AWAY'),
    ('PICKING', 'PICKING'),
    ('PACKING', 'PACKING'),
    ('DISPATCHING', 'DISPATCHING'),
    ('SHIPPING', 'SHIPPING'),
    ('STORAGE', 'STORAGE'),
    ('RETURNS', 'RETURNS'),
    ('VALUE ADDING', 'VALUE ADDING'),
)

SALES = 'SALES'
ADD = 'ADD'
REMOVE = 'REMOVE'
INVENTORY = 'INVENTORY'
PRIVATE = 'PRIVATE'
STORAGE = 'STORAGE'


class WarehouseItem(AbstractBase):
    """Warehouse Item model."""

    item = models.OneToOneField(
        Item, null=False, blank=False, on_delete=PROTECT, unique=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    @property
    def summary(self):
        """Get summary."""
        store_records = WarehouseRecord.objects.filter(
            warehouse_item=self, enterprise=self.enterprise)
        total_quantity = 0
        total_amount = 0
        for store_record in store_records:
            if store_record.closing_quantity >= total_quantity:
                total_quantity = store_record.closing_quantity

            if store_record.closing_total_amount >= total_amount:
                total_amount = store_record.closing_total_amount

        summary = {
            'total_quantity': total_quantity,
            'total_amount': total_amount,
        }

        return summary

    @property
    def quantity(self):
        """Get quantity."""
        store_record = WarehouseRecord.objects.filter(warehouse_item=self)
        if not store_record.exists():
            return 0

        latest_record = store_record.latest('updated_on')
        return latest_record.closing_quantity

    @property
    def total_amount(self):
        """Get total amount."""
        store_record = WarehouseRecord.objects.filter(warehouse_item=self)
        if not store_record.exists():
            return 0

        latest_record = store_record.latest('updated_on')
        return latest_record.closing_total_amount

    def clean(self) -> None:
        """Clean store model."""
        return super().clean()

    def __str__(self):
        """Str representation for the store_item."""
        return '{}'.format(self.item.item_name)

    class Meta:
        """Meta class for inventory."""

        ordering = ['item__item_name']


class Warehouse(AbstractBase):
    """Warehouse model."""

    warehouse_code = models.CharField(max_length=250, null=True, blank=True)
    warehouse_name = models.CharField(max_length=300)
    warehouse_type = models.CharField(
        max_length=300, choices=WAREHOUSE_TYPE_CHOICES, default=PRIVATE)
    warehouse_items = models.ManyToManyField(
        WarehouseItem, through='WarehouseWarehouseItem', related_name='warehousewarehouseitems')
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_receiving = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    pushed_to_edi = models.BooleanField(default=False)

    def get_warehouse_item_summary(self, warehouse_item):
        """Get warehouse item summary."""
        summary = {
            'opening_quantity': 0,
            'opening_total_amount': 0,
            'quantity_recorded': 0,
            'total_amount_recorded': 0,
            'closing_quantity': 0,
            'closing_total_amount': 0,
        }
        records = WarehouseRecord.objects.filter(
            warehouse=self, warehouse_item=warehouse_item)

        if not records.exists():
            return summary

        latest_record = records.latest('record_date')
        summary['opening_quantity'] = latest_record.opening_quantity
        summary['opening_total_amount'] = latest_record.opening_total_amount
        summary['quantity_recorded'] = latest_record.quantity_recorded
        summary['total_amount_recorded'] = latest_record.total_amount_recorded
        summary['closing_quantity'] = latest_record.closing_quantity
        summary['closing_total_amount'] = latest_record.closing_total_amount
        return summary


class WarehouseWarehouseItem(AbstractBase):
    """Warehouse Warehouse Items model."""

    warehouse = models.ForeignKey(
        Warehouse, on_delete=models.PROTECT)
    warehouse_item = models.ForeignKey(
        WarehouseItem, on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)
    pushed_to_edi = models.BooleanField(default=False)


class WarehouseRecord(AbstractBase):
    """Warehouse model."""

    record_date = models.DateTimeField(db_index=True, default=timezone.now)
    warehouse = models.ForeignKey(
        Warehouse, null=False, blank=False, on_delete=models.PROTECT)
    warehouse_item = models.ForeignKey(
        WarehouseItem, null=False, blank=False, on_delete=models.PROTECT)
    opening_quantity = models.FloatField(default=0.0)
    opening_total_amount = models.FloatField(default=0.0)
    warehouse_process = models.CharField(
        max_length=300, choices=WAREHOUSE_PROCESS_CHOICES, default=STORAGE)
    record_type = models.CharField(
        max_length=300, null=False, blank=False,
        choices=RECORD_TYPE_CHOICES, default=ADD)
    quantity_recorded = models.FloatField(null=False, blank=False)
    removal_type = models.CharField(
        max_length=300, null=True, blank=True, choices=REMOVE_FROM_WAREHOUSE_CHOICES)
    removal_guid = models.UUIDField(null=True, blank=True)
    addition_guid = models.UUIDField(null=True, blank=True)
    unit_price = models.FloatField(null=True, blank=True)
    disposing_price = models.FloatField(null=True, blank=True)
    total_amount_recorded = models.FloatField(null=True, blank=True)
    closing_quantity = models.FloatField(null=True, blank=True)
    closing_total_amount = models.FloatField(null=True, blank=True)
    removal_quantity_leaving_warehouse = models.FloatField(null=True, blank=True, default=0)
    removal_quantity_remaining_in_warehouse = models.FloatField(null=True, blank=True, default=0)
    # clean to create inventory record if removal type is inventory

    def get_unit_price(self):
        """Get unit price."""
        if not self.unit_price:
            inventory_item = InventoryItem.objects.filter(item=self.warehouse_item.item)
            if not inventory_item.exists():
                self.unit_price = 0
            else:
                inventory_item = inventory_item.first()
                self.unit_price = inventory_item.unit_price

    def get_opening_records(self):
        """Initialize opening records."""
        records = self.__class__.objects.filter(
            warehouse=self.warehouse, warehouse_item=self.warehouse_item)
        if records.exists():
            latest_record = records.latest('record_date')
            self.opening_quantity = latest_record.closing_quantity
            self.opening_total_amount = latest_record.closing_total_amount

    def validate_removal_type(self):
        """Validate removal type."""
        if self.record_type == REMOVE:
            if not self.removal_type:
                raise ValidationError(
                    {'removal type': 'Please specify the removal type of this item from store'})

    def validate_unique_addition_guid(self):
        """Validate a record is created once from the given source."""
        if self.addition_guid and self.__class__.objects.filter(
                record_type=self.record_type,
                addition_guid=self.addition_guid).exclude(id=self.id).exists():
            msg = "A similar warehouse record from this source already exists, \
                please audit your entries"
            raise ValidationError({"removal": msg})

    def validate_unique_removal_guid(self):
        """Validate a record is created once from the given source."""
        if self.removal_guid and self.__class__.objects.filter(
                removal_guid=self.removal_guid).exclude(id=self.id).exists():
            msg = "A similar warehouse record to this destination already exists, \
                please audit your entries"
            raise ValidationError({"removal": msg})

    def validate_removed_items_exist(self):
        """Validate removal item exists."""
        if self.record_type == REMOVE and not self.removal_guid:
            if self.quantity_recorded > self.opening_quantity:
                if self.opening_quantity == 0.0:
                    raise ValidationError(
                        {'quantity': 'The store is currently empty. Please add items to tranfer items from it'})    # noqa

                raise ValidationError(
                    {'quantity': f'Only {self.opening_quantity} are in store which are less than the items you want to transfer'})  # noqa

    def calculate_total_amount_recorded(self):
        """Calculate total amount recorded."""
        if not self.disposing_price:
            total = float(self.quantity_recorded) * float(self.unit_price)
            self.total_amount_recorded = total
        else:
            total = self.quantity_recorded * self.disposing_price
            self.total_amount_recorded = total

    def calculate_closing_records(self):
        """Calculate closing quantity and amounts."""
        if self.record_type == ADD:
            quantity = self.opening_quantity + self.quantity_recorded
            total = self.opening_total_amount + self.total_amount_recorded
            self.closing_quantity = quantity
            self.closing_total_amount = total

        if self.record_type == REMOVE:
            quantity = self.opening_quantity - self.quantity_recorded
            total = self.opening_total_amount - self.total_amount_recorded
            self.closing_quantity = quantity
            self.closing_total_amount = total

    def clean(self) -> None:
        """Clean Store record model."""
        self.get_opening_records()
        self.validate_removal_type()
        self.validate_unique_addition_guid()
        self.validate_unique_removal_guid()
        self.validate_removed_items_exist()
        self.calculate_closing_records()
        return super().clean()

    def process_removal(self):
        """Process removals from store."""
        from elites_retail_portal.enterprise_mgt.models import (
            EnterpriseSetupRule)
        if not self.record_type == REMOVE:
            return

        if self.removal_type == INVENTORY:
            enterprise_setup_rules = EnterpriseSetupRule.objects.get(
                enterprise=self.enterprise, is_active=True)
            default_inventory = enterprise_setup_rules.default_inventory
            audit_fields = {
                'created_by': self.created_by,
                'updated_by': self.updated_by,
                'enterprise': self.enterprise,
            }
            inventory_items = InventoryItem.objects.filter(
                item=self.warehouse_item.item, enterprise=self.enterprise, is_active=True)
            inventory_item = inventory_items.first()
            if not inventory_items.exists():
                inventory_item = InventoryItem.objects.create(
                    item=self.warehouse_item.item, **audit_fields)

            if not InventoryInventoryItem.objects.filter(
                    inventory=default_inventory, inventory_item=inventory_item,
                    enterprise=self.enterprise).exists():
                InventoryInventoryItem.objects.create(
                    inventory=default_inventory, inventory_item=inventory_item, **audit_fields)

            inventory_items = default_inventory.inventory_items.filter(id=inventory_item.id)
            inventory_item = inventory_items.first()

            inventory_record = InventoryRecord.objects.filter(addition_guid=self.id).first()

            if inventory_record:
                inventory_record.inventory = default_inventory
                inventory_record.inventory_item = inventory_item
                inventory_record.quantity_recorded = self.quantity_recorded
                inventory_record.unit_price = self.unit_price
                inventory_record.updated_by = self.updated_by
                inventory_record.quantity_of_stock_on_display = self.removal_quantity_leaving_warehouse     # noqa
                inventory_record.quantity_of_stock_in_warehouse = self.removal_quantity_remaining_in_warehouse    # noqa
                inventory_record.save()
                self.__class__.objects.filter(id=self.id).update(removal_guid=inventory_record.id)
            else:
                payload = {
                    "inventory": default_inventory,
                    "inventory_item": inventory_item,
                    "quantity_recorded": self.quantity_recorded,
                    "unit_price": self.unit_price,
                    "record_type": ADD,
                    "addition_guid": self.id,
                    "quantity_of_stock_on_display": self.removal_quantity_leaving_warehouse,
                    "quantity_of_stock_in_warehouse": self.removal_quantity_remaining_in_warehouse
                }
                inventory_record = InventoryRecord.objects.create(**payload, **audit_fields)
                self.__class__.objects.filter(id=self.id).update(removal_guid=inventory_record.id)

    def save(self, *args, **kwargs):
        """Perform pre save and post save actions."""
        if self.record_type == REMOVE and not self.removal_quantity_remaining_in_warehouse:
            self.removal_quantity_remaining_in_warehouse = (
                self.quantity_recorded - self.removal_quantity_leaving_warehouse)
        self.get_unit_price()
        self.calculate_total_amount_recorded()
        super().save(*args, **kwargs)
        self.process_removal()
