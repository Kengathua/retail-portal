"""Inventory models file."""

from tokenize import Triple
from django.db import models
from django.db.models import PROTECT
from django.core.exceptions import ValidationError

from elites_franchise_portal.items.models import Item
from elites_franchise_portal.common.models import AbstractBase

REMOVE_FROM_INVENTORY_CHOICES = (
    ('SALES', 'SALES'),
    ('DAMAGES', 'DAMAGES'),
    ('RETURNS', 'RETURNS'),
    ('SUPPLIES', 'SUPPLIES'),
    ('INVENTORY', 'INVENTORY'),
)

RECORD_TYPE_CHOICES = (
    ('ADD', 'ADD'),
    ('REMOVE', 'REMOVE'),
)

INVENTORY_TYPE_CHOICES = (
    ('EXCESS', 'EXCESS'),
    ('SERVICE', 'SERVICE'),
    ('AVAILABLE', 'AVAILABLE'),
    ('ALLOCATED', 'ALLOCATED'),
    ('DECOUPLING', 'DECOUPLING'),
    ('THEORETICAL', 'THEORETICAL'),
    ('RAW MATERIALS', 'RAW MATERIALS'),
    ('FINISHED GOODS', 'FINISHED GOODS'),
    ('MAINTENANCE, REPAIR AND OPERATING', 'MRO'),
    ('SAFETY STOCK', 'SAFETY STOCK'),
    ('WORKING STOCK', 'WORKING STOCK'),
    ('ANTICIPATORY STOCK', 'ANTICIPATORY STOCK'),
    ('PSYCHIC STOCK', 'PSYCHIC STOCK'),
    ('PACKING MATERIALS', 'PACKING MATERIALS'),
    ('IN TRANSIT STOCK', 'IN TRANSIT STOCK'),
    ('WORK IN PROCESS', 'WORK IN PROCESS'),
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
    check_warehouse = models.BooleanField(default=True)

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
        return 0

    @property
    def total_amount(self):
        """Get the total amount of item in inventory."""
        return 0

    @property
    def unit_price(self):
        """Get the unit price."""
        record = InventoryRecord.objects.filter(inventory_item=self).first()
        return record.unit_price if record else 0

    def check_item_in_warehouse(self):
        """Check item exists in store."""
        from .import WarehouseItem
        warehouse_item_exists = WarehouseItem.objects.filter(item=self.item).exists()
        if not warehouse_item_exists:
            data = {
                'updated_by': self.updated_by,
                'created_by': self.created_by,
                'item': self.item,
                'franchise': self.franchise,
            }
            WarehouseItem.objects.create(**data)

    def check_item_in_catalog_items(self, section):
        """Check that item exists in catalog items."""
        from elites_franchise_portal.catalog.models import CatalogItem
        data = {
            'updated_by': self.updated_by,
            'created_by': self.created_by,
            'franchise': self.franchise,
            'marked_price': self.unit_price,
            'selling_price': self.unit_price,
            'quantity': self.summary['available_quantity'],
            'section': section,
            }
        defaults = {
            'inventory_item': self,
            'franchise': self.franchise,
            }
        CatalogItem.objects.update_or_create(defaults=defaults, **data)

    def __str__(self):
        """Str representation for the inventory_item."""
        return '{}'.format(self.item.item_name)

    def save(self, *args, **kwargs):
        """Super save to perform pre and post save."""
        super().save(*args, **kwargs)
        inventory = Inventory.objects.filter(
            is_master=True, is_active=True, franchise=self.franchise)
        inventory = inventory.first()
        if inventory:
            audit_fields = {
                'updated_by': self.updated_by,
                'created_by': self.created_by,
                'franchise': self.franchise
                }

            InventoryInventoryItem.objects.filter(inventory=inventory, inventory_item=self, **audit_fields)

    class Meta:
        """Meta class for inventory model."""

        ordering = ['item__item_name']


class Inventory(AbstractBase):
    """Inventory model."""

    inventory_name = models.CharField(max_length=300)
    inventory_code = models.CharField(max_length=300, null=True, blank=True)
    inventory_type = models.CharField(
        max_length=300, choices=INVENTORY_TYPE_CHOICES, default=WORKING_STOCK)
    inventory_items =  models.ManyToManyField(
        InventoryItem, through='InventoryInventoryItem', related_name='inventoryinventoryitems')
    is_master = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    pushed_to_edi = models.BooleanField(default=False)

    @property
    def summary(self):
        inventory_items = self.inventory_items.all()
        inventory_records = InventoryRecord.objects.filter(
            inventory=self, inventory_item__in=inventory_items, franchise=self.franchise)

        summary = []
        if inventory_records.exists():
            for inventory_item in inventory_items:
                try:
                    latest_inventory_item_record = inventory_records.filter(inventory_item=inventory_item).latest('updated_on')
                    quantity = latest_inventory_item_record.closing_stock_quantity
                    total_amount = latest_inventory_item_record.closing_stock_total_amount
                    data = {
                        'inventory_item': inventory_item,
                        'quantity':quantity,
                        'total_amount':total_amount,
                        }
                    summary.append(data)
                except Exception:
                    pass

        return summary

    def validate_unique_active_master_inventory_for_franchise(self):
        inventory = self.__class__.objects.filter(id=self.id)
        if not inventory.exists():
            # It is a new inventory being created
            if self.is_master and self.__class__.objects.filter(
                is_active=True, is_master=True, franchise=self.franchise).exists():
                msg = 'You can only have one active master inventory'
                raise ValidationError({'inventory': msg})

    def validate_unique_active_available_inventory_for_franchise(self):
        inventory = self.__class__.objects.filter(id=self.id)
        if not inventory.exists():
            # It is a new inventory being created
            if self.__class__.objects.filter(
                is_active=True, inventory_type=AVAILABLE, franchise=self.franchise).exists():
                msg = 'You can only have one active available inventory'
                raise ValidationError({'inventory': msg})

    def validate_unique_active_allocated_inventory_for_franchise(self):
        inventory = self.__class__.objects.filter(id=self.id)
        if not inventory.exists():
            # It is a new inventory being created
            if self.__class__.objects.filter(
                is_active=True, inventory_type=ALLOCATED, franchise=self.franchise).exists():
                msg = 'You can only have one active allocated inventory'
                raise ValidationError({'inventory': msg})

    def clean(self) -> None:
        self.validate_unique_active_master_inventory_for_franchise()
        self.validate_unique_active_available_inventory_for_franchise()
        self.validate_unique_active_allocated_inventory_for_franchise()
        return super().clean()

class InventoryInventoryItem(AbstractBase):
    """Inventory Invetory Item model."""

    inventory = models.ForeignKey(Inventory, on_delete=models.PROTECT)
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)
    pushed_to_edi = models.BooleanField(default=False)


class InventoryRecord(AbstractBase):
    """Inventory Record class."""

    inventory = models.ForeignKey(Inventory, on_delete=models.PROTECT)
    inventory_item = models.ForeignKey(
        InventoryItem, null=False, blank=False, on_delete=PROTECT)
    record_code = models.CharField(max_length=300, null=True, blank=True)
    opening_stock_quantity = models.FloatField(null=True, blank=True, default=0)
    opening_stock_total_amount = models.FloatField(null=True, blank=True, default=0)
    record_type = models.CharField(max_length=300, choices=RECORD_TYPE_CHOICES, default=ADD)
    quantity_recorded = models.FloatField(null=False, blank=False)
    unit_price = models.FloatField(null=False, blank=False)
    total_amount_recorded = models.FloatField(null=True, blank=True)
    removal_type = models.CharField(
        max_length=300, null=True, blank=True, choices=REMOVE_FROM_INVENTORY_CHOICES)
    closing_stock_quantity = models.FloatField(null=True, blank=True, default=0)
    closing_stock_total_amount = models.FloatField(null=True, blank=True, default=0)
    quantity_of_stock_on_display = models.FloatField(null=True, blank=True)
    quantity_of_stock_in_warehouse = models.FloatField(null=True, blank=True)
    quantity_of_stock_on_sale = models.FloatField(null=True, blank=True)
    quantity_sold = models.FloatField(null=True, blank=True)
    remaining_stock_total_amount = models.FloatField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def get_latest_record(self, record_type=None):
        record = None
        record_type = record_type if record_type else self.record_type
        records = InventoryRecord.objects.filter(
            inventory=self.inventory, inventory_item=self.inventory_item, record_type=record_type,
            franchise=self.franchise)
        if records:
            record = records.latest('updated_on')

        return record

    def validate_inventory_item_exists_in_inventory(self):
        if not InventoryInventoryItem.objects.filter(
            inventory=self.inventory, inventory_item=self.inventory_item,
            is_active=True).exists():
            inventory = self.inventory.inventory_type.title()
            inventory_item = self.inventory_item.item.item_name
            raise ValidationError(
                {'inventory_item': f'{inventory_item} is not hooked up to an active instance '
                 'of the {inventory} Inventory. Please set that up first'})

    def get_opening_stock(self):
        """Initialize opening stock."""
        records = self.__class__.objects.filter(
            inventory=self.inventory, inventory_item=self.inventory_item)
        if records.exists():
            latest_record = records.latest('updated_on')
            self.opening_stock_quantity = latest_record.closing_stock_quantity
            self.opening_stock_total_amount = latest_record.closing_stock_total_amount
        else:
            self.opening_stock_quantity = 0.0
            self.opening_stock_total_amount = 0.0

    def validate_removal_type(self):
        """Validate removal item has removal type."""
        if self.record_type == REMOVE:
            if not self.removal_type:
                raise ValidationError(
                    {'removal type': 'Please specify the removal type of this item from inventory'})    # noqa

    def calculate_total_amount_recorded(self):
        """Calculate total amount recorded."""
        total = self.quantity_recorded * self.unit_price
        self.total_amount_recorded = total

    def calculate_closing_stock_quantity(self):
        """Calculate quantity of closing stock."""
        if self.record_type == ADD:
            recorded_quantity = self.quantity_recorded
            recorded_total_amount = self.total_amount_recorded

        if self.record_type == REMOVE:
            recorded_quantity = -(self.quantity_recorded)
            latest_add = self.get_latest_record('ADD')
            recorded_total_amount = -(latest_add.unit_price * self.quantity_recorded)

        self.closing_stock_quantity = self.opening_stock_quantity + recorded_quantity
        self.closing_stock_total_amount = self.opening_stock_total_amount + recorded_total_amount

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
        available_quantity = self.opening_stock_quantity
        if self.record_type == REMOVE and self.quantity_recorded > available_quantity:
            raise ValidationError(
                {'quantity': f'You are trying to remove {self.quantity_recorded} items and the inventory has {available_quantity} items'})  # noqa

    def validate_removal_item_has_removal_type(self):
        """Validate removal item has a removal type."""
        if self.record_type == REMOVE:
            if not self.removal_type:
                raise ValidationError(
                    {'removal_type': 'Please specify where to the items are being taken to from the inventory'})    # noqa

    def validate_unique_record_code(self):
        """Validate record code is unique for the inventory."""
        record = self.__class__.objects.filter(inventory=self.inventory, record_code=self.record_code)
        if record.exclude(id=self.id).exists():
            import pdb
            pdb.set_trace()
            raise ValidationError(
                {'record_code': 'A record with this record code already exists. Please supply a unique record code'})

    def clean(self) -> None:
        """Clean Inventory Record."""
        self.validate_inventory_item_exists_in_inventory()
        self.validate_cannot_remove_more_than_existing_items()
        self.validate_removal_item_has_removal_type()
        self.validate_unique_record_code()
        return super().clean()

    def update_catalog_item(self):
        """Update Catalog item."""
        from elites_franchise_portal.catalog.models import CatalogItem
        catalog_items = CatalogItem.objects.filter(
            inventory_item=self.inventory_item, franchise=self.franchise)
        catalog_item = catalog_items.first()
        if catalog_items.exists():
            filters = {
                    'id': catalog_item.id,
                    'franchise': catalog_item.franchise,
                }
            if self.record_type == ADD:
                quantity = catalog_item.quantity + self.quantity_recorded
                return catalog_items.update(
                    marked_price=self.unit_price, quantity=quantity, **filters)

            if self.record_type == REMOVE:
                marked_price = catalog_item.marked_price
                quantity = catalog_item.quantity - self.quantity_recorded
                return catalog_items.update(
                    marked_price=marked_price, quantity=quantity, **filters)

    def update_master_inventory(self):
        audit_fields = {
            'created_by': self.created_by,
            'updated_by': self.updated_by,
            'franchise': self.franchise}
        if self.inventory.inventory_type == AVAILABLE:
            master_inventory = Inventory.objects.get(is_master=True, is_active=True, franchise=self.franchise)
            record = self.__class__.objects.get(id=self.id)
            data = {
                'inventory': master_inventory,
                'record_code':record.record_code,
                'quantity_recorded': record.quantity_recorded,
                'inventory_item': record.inventory_item,
                'record_type': record.record_type,
                'unit_price': record.unit_price,
                'removal_type': record.removal_type,
                'quantity_sold': record.quantity_sold,
                'total_amount_recorded': record.total_amount_recorded,
            }
            if InventoryRecord.objects.filter(
                inventory=master_inventory, record_code=record.record_code,
                franchise=record.franchise).exists():
                return self.__class__.objects.update(**data, **audit_fields)

            return self.__class__.objects.create(**data, **audit_fields)

    def save(self, *args, **kwargs):
        """Perform pre save and post save actions on Catalog Item."""
        # NOTE the order
        if not self.record_code:
            from random import randint
            self.record_code = str(randint(10000, 10000000))
        self.get_opening_stock()
        self.calculate_total_amount_recorded()
        self.calculate_closing_stock_quantity()
        super().save(*args, **kwargs)
        self.update_catalog_item()
        self.update_master_inventory()

    class Meta:
        """Meta class for Base Inventory class."""

        ordering = ['inventory_item__item__item_name']
