"""Catalog model file."""

from decimal import Decimal
from django.db import models
from django.core.cache import cache
from django.utils import timezone
from django.core.exceptions import ValidationError

from elites_retail_portal.common.choices import CURRENCY_CHOICES
from elites_retail_portal.debit.models import (
    Inventory, InventoryItem, InventoryRecord)
from elites_retail_portal.items.models import (
    ItemUnits, ItemAttribute, Product)
from elites_retail_portal.common.models import AbstractBase
from elites_retail_portal.common.validators import (
    items_enterprise_code_validator)
from elites_retail_portal.customers.models import Customer
from django.contrib.auth import get_user_model
from elites_retail_portal.users.models import retrieve_user_email
from elites_retail_portal.common.code_generators import (
    generate_enterprise_code)
from django.core.validators import MinValueValidator

KSH = 'KSH'

ON_SITE = 'ON SITE'

CATALOG_TYPE_CHOICES = (
    ('ON SITE', 'ON SITE'),
    ('AGENTS', 'AGENTS'),
    ('CUSTOMERS', 'CUSTOMERS'),
)

AUDIT_RECORD_TYPE_CHOICES = (
    ('ADD', 'ADD'),
    ('REMOVE', 'REMOVE')
)

AUDIT_OPERATIONS_TYPE_CHOICES = (
    ('CREATE CATALOG ITEM', 'CREATE CATALOG ITEM'),
    ('UPDATE CATALOG ITEM', 'UPDATE CATALOG ITEM'),
    ('CREATE INVENTORY RECORD', 'CREATE INVENTORY RECORD'),
    ('UPDATE INVENTORY RECORD', 'UPDATE INVENTORY RECORD'),
)

AUDIT_TYPE_CHOICES = (
    ('CREATE', 'CREATE'),
    ('UPDATE', 'UPDATE')
)

CATALOG_ITEM_AUDIT_SOURCES = (
    ('CATALOG ITEM', 'CATALOG ITEM'),
    ('INVENTORY RECORD', 'INVENTORY RECORD')
)

INVENTORY_RECORD = 'INVENTORY RECORD'
CREATE_CATALOG_ITEM = 'CREATE CATALOG ITEM'


class Section(AbstractBase):
    """Sections for items in the premise."""

    section_name = models.CharField(
        null=False, blank=False, max_length=250)
    section_code = models.CharField(
        max_length=250, null=True, blank=True, validators=[items_enterprise_code_validator])
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    creator = retrieve_user_email('created_by')
    updater = retrieve_user_email('updated_by')

    def create_section_code(self):
        """Create section code."""
        if not self.section_code:
            self.section_code = generate_enterprise_code(self)

    def clean(self) -> None:
        """Clean section model."""
        # validate_enterprise_exists(self)
        self.create_section_code()
        return super().clean()

    def __str__(self):
        """Str representation for the section model."""
        return '{}'.format(
            self.section_name,
            )

    class Meta:
        """Meta class for section model."""

        ordering = ['-section_name']


class CatalogItem(AbstractBase):
    """Catalog item model."""

    inventory_item = models.OneToOneField(
        InventoryItem, null=False, blank=False, unique=True, on_delete=models.CASCADE)
    section = models.ForeignKey(
        Section, null=False, blank=False, on_delete=models.CASCADE)
    marked_price = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=True, blank=True)
    discount_amount = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=True, blank=True, default=0)
    selling_price = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=True, blank=True)
    threshold_price = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=True, blank=True)
    currency = models.CharField(
        null=False, blank=False, max_length=250, choices=CURRENCY_CHOICES, default=KSH)
    quantity = models.FloatField(default=0)
    on_display = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    pushed_to_edi = models.BooleanField(default=False)
    creator = retrieve_user_email('created_by')
    updater = retrieve_user_email('updated_by')

    @property
    def products(self):
        """Get products."""
        products = Product.objects.filter(
            item=self.inventory_item.item, status="ON SALE", is_active=True)
        if products.exists():
            return products
        return Product.objects.none()

    @property
    def catalogs_names(self):
        """Get catalog names."""
        names = ''
        catalog_catalog_items = CatalogCatalogItem.objects.filter(
                catalog_item=self, is_active=True)
        if catalog_catalog_items.exists():
            names = list(
                set(catalog_catalog_items.values_list('catalog__catalog_name', flat=True)))
            names = ", ".join(names)
        return names

    @property
    def item_heading(self):
        """Compose an item heading to display item."""
        type = self.inventory_item.item.item_model.item_type.type_name
        brand = self.inventory_item.item.item_model.brand.brand_name
        model = self.inventory_item.item.item_model.model_name

        item_units = ItemUnits.objects.filter(item=self.inventory_item.item).first()
        units = item_units.sales_units.units_name if item_units else ''

        special_features = []
        special_offers = []
        year = ''

        item_attributes = ItemAttribute.objects.filter(
            item=self.inventory_item.item)
        if item_attributes.exists():
            special_features = item_attributes.last().special_features
            special_offers = item_attributes.last().special_offers

        special_offer = ''
        if special_offers:
            str_special_offers = ", ".join(special_offers)
            special_offer = ' {}'.format(str_special_offers)

        str_special_features = ''
        if special_features:
            str_special_features = ", ".join(special_features)

        item_heading = brand + ' ' + model + ' ' + \
            str_special_features + ' ' + type + ', ' + \
            year + units + special_offer

        return item_heading

    def get_marked_price(self):
        """Get marked price."""
        if not self.marked_price:
            self.marked_price = Decimal(self.inventory_item.unit_price)

    def get_selling_price(self):
        """Initialize the selling price."""
        self.selling_price = Decimal(
            float(self.marked_price) - float(self.discount_amount or 0))

    def get_threshold_price(self):
        """Get threshold price."""
        if not self.threshold_price or self.threshold_price > self.selling_price:
            self.threshold_price = self.selling_price

    def get_quantity(self):
        """Get quantity."""
        from elites_retail_portal.enterprise_mgt.helpers import (
            get_valid_enterprise_setup_rules)
        inventories = Inventory.objects.filter(is_active=True, enterprise=self.enterprise)

        if inventories.exists() and not inventories.filter(is_master=True).exists():
            raise ValidationError(
                {'inventory':
                    'Your enterprise does not have a master Inventory. Please set up one first'})

        quantity = 0
        enterprise_setup_rules = get_valid_enterprise_setup_rules(self.enterprise)
        available_inventory = enterprise_setup_rules.available_inventory
        if not available_inventory.summary == []:
            quantities = [
                data['quantity'] for data in available_inventory.summary
                if data['inventory_item'] == self.inventory_item]

            quantity = quantities[0] if quantities else 0

        self.quantity = quantity
        return quantity

    # TODO Add user to this functionality to use the user instead of the catalog item updater
    def add_to_cart(
            self, customer=None, price=None,
            quantity=None, is_installment=False, order_now=False):
        """Add item to cart."""
        from elites_retail_portal.orders.models import Cart, CartItem
        if not customer:
            user = get_user_model().objects.get(id=self.updated_by)
            customer = Customer.objects.filter(enterprise_user=user).first()
        cart = Cart.objects.filter(customer=customer)
        if not cart.exists():
            cart_data = {
                'created_by': self.created_by,
                'updated_by': self.updated_by,
                'enterprise': self.enterprise,
                'customer': customer,
            }
            Cart.objects.create(**cart_data)
        cart = Cart.objects.get(customer=customer, is_active=True)

        cart_item = CartItem.objects.filter(
            cart=cart, catalog_item=self, enterprise=self.enterprise).first()
        if price:
            if price < self.threshold_price:
                diff = float(self.threshold_price) - float(price)
                raise ValidationError(
                    {'price': 'The selling price {} {} is below the threshold price {} {} '
                     'by {} {}'.format(
                         self.currency, price, self.currency,
                         self.threshold_price, self.currency, diff)})

            cart_item.selling_price = price

        if not cart_item:
            cart_item_data = {
                'created_by': self.created_by,
                'updated_by': self.updated_by,
                'enterprise': self.enterprise,
                'cart': cart,
                'selling_price': price if price else self.selling_price,
                'catalog_item': self,
                'quantity_added': 1 if not quantity else quantity,
                'is_installment': is_installment,
                'order_now': order_now,
            }
            cart_item = CartItem.objects.create(**cart_item_data)
            return cart_item

        cart_item.quantity_added = 1 if not quantity else quantity
        cart_item.is_installment = is_installment
        cart_item.order_now = order_now
        cart_item.save()
        return cart_item

    def validate_item_is_active(self):
        """Remove item from cart."""
        item_units = ItemUnits.objects.filter(item=self.inventory_item.item, is_active=True)
        if not item_units.exists():
            msg = 'The {} does not have active units'.format(
                self.inventory_item.item.item_name)

            raise ValidationError(
                {'item_units': msg})

    def add_to_catalogs(self, user, catalogs):
        """Add catalog item to the specified catalogs."""
        if not catalogs:
            msg = 'Please select the catalogs you want to add the item to'
            raise ValidationError({'catalogs': msg})
        audit_fields = {
            'created_by': user.id,
            'updated_by': user.id,
            'enterprise': user.enterprise,
        }
        for catalog in catalogs:
            if not CatalogCatalogItem.objects.filter(
                    catalog=catalog, catalog_item=self).exists():
                CatalogCatalogItem.objects.create(
                    catalog=catalog, catalog_item=self, **audit_fields)

    def clean(self) -> None:
        """Clean Catalog Item."""
        self.validate_item_is_active()
        return super().clean()

    def __str__(self):
        """Str representation for the section model."""
        return '{}'.format(
            self.inventory_item.item.item_name,
            )

    def save(self, *args, **kwargs):
        """Perform pre save and post save actions."""
        if not self.quantity:
            self.get_quantity()
        self.get_marked_price()
        self.get_selling_price()
        self.get_threshold_price()
        super().save(*args, **kwargs)
        if not Product.objects.filter(
                item=self.inventory_item.item, enterprise=self.enterprise).exists():
            payload = {
                'created_by': self.created_by,
                'updated_by': self.updated_by,
                'enterprise': self.enterprise,
                'item': self.inventory_item.item,
                'serial_number': None,
            }
            Product.objects.create(**payload)

        if not CatalogItemAuditLog.objects.filter(catalog_item=self).exists():
            CatalogItemAuditLog.objects.create(
                catalog_item=self, quantity_recorded=self.quantity,
                marked_price_recorded=self.marked_price,
                discount_amount_recorded=self.discount_amount,
                selling_price_recorded=self.selling_price,
                threshold_price_recorded=self.threshold_price,
                record_type='ADD', operation_type=CREATE_CATALOG_ITEM,
                audit_type='CREATE',
                audit_source='CATALOG ITEM', created_by=self.created_by,
                updated_by=self.updated_by, enterprise=self.enterprise)

        cache.delete('catalog_items_objects')

    class Meta:
        """Meta class for catalog."""

        ordering = ['-marked_price', '-selling_price', '-inventory_item']
    # TODO clean to check if item has restrictions (on_deposit) -> clearing
    # TODO clean to check if that specific item is on (barcode)
    # TODO Add an endpoint to remove item from catalog
    # TODO auto calculate selling price given marked price and discount
    # TODO validate item exists in inventory


class Catalog(AbstractBase):
    """Catalog model."""

    # TODO Add a short name field
    catalog_name = models.CharField(max_length=300, null=False, blank=False)
    catalog_code = models.CharField(max_length=300, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_standard = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    deactivated_on = models.DateTimeField(null=True, blank=True)
    deactivation_reason = models.TextField(null=True, blank=True)
    catalog_type = models.CharField(max_length=300, choices=CATALOG_TYPE_CHOICES, default=ON_SITE)
    catalog_items = models.ManyToManyField(
        CatalogItem, through='CatalogCatalogItem',
        related_name='catalogitem')
    is_active = models.BooleanField(default=True)
    pushed_to_edi = models.BooleanField(default=False)

    def __str__(self):
        """Str representation for the section model."""
        return '{}'.format(
            self.catalog_name,
            )


class CatalogCatalogItem(AbstractBase):
    """Catalog Item Catalog."""

    catalog = models.ForeignKey(
        Catalog,
        on_delete=models.CASCADE,
        related_name='catalog_catalogcatalogitem')
    catalog_item = models.ForeignKey(
        CatalogItem,
        on_delete=models.CASCADE,
        related_name='catalog_item_catalogcatalogitem')
    is_active = models.BooleanField(default=True)
    pushed_to_edi = models.BooleanField(default=False)


class CatalogItemAuditLog(AbstractBase):
    """Catalog Item Log Audit Log."""

    catalog_item = models.ForeignKey(
        CatalogItem, on_delete=models.PROTECT,
        related_name='catalog_item_audit_log')
    audit_date = models.DateTimeField(db_index=True, default=timezone.now)
    quantity_before = models.FloatField(null=True, blank=True, default=0)
    quantity_recorded = models.FloatField(null=True, blank=True, default=0)
    quantity_after = models.FloatField(null=True, blank=True, default=0)
    selling_price_before = models.FloatField(null=True, blank=True, default=0)
    selling_price_recorded = models.FloatField(null=True, blank=True, default=0)
    selling_price_after = models.FloatField(null=True, blank=True, default=0)
    marked_price_before = models.FloatField(null=True, blank=True, default=0)
    marked_price_recorded = models.FloatField(null=True, blank=True, default=0)
    marked_price_after = models.FloatField(null=True, blank=True, default=0)
    threshold_price_before = models.FloatField(null=True, blank=True, default=0)
    threshold_price_recorded = models.FloatField(null=True, blank=True, default=0)
    threshold_price_after = models.FloatField(null=True, blank=True, default=0)
    discount_amount_before = models.FloatField(null=True, blank=True, default=0)
    discount_amount_recorded = models.FloatField(null=True, blank=True, default=0)
    discount_amount_after = models.FloatField(null=True, blank=True, default=0)
    record_type = models.CharField(max_length=300, choices=AUDIT_RECORD_TYPE_CHOICES)
    operation_type = models.CharField(max_length=300, choices=AUDIT_OPERATIONS_TYPE_CHOICES)
    audit_type = models.CharField(max_length=300, choices=AUDIT_TYPE_CHOICES)
    audit_source = models.CharField(
        max_length=300, choices=CATALOG_ITEM_AUDIT_SOURCES, default=INVENTORY_RECORD)
    inventory_record = models.ForeignKey(
        InventoryRecord, null=True, blank=True, on_delete=models.PROTECT)

    def get_quantity_after(self):
        """Get quantity after addition."""
        if not self.quantity_after:
            self.quantity_after = self.quantity_before + self.quantity_recorded

    def get_amounts(self):
        """Get amounts."""
        if self.record_type == 'REMOVE' or self.audit_type == "UPDATE" and\
                not self.audit_source == 'CATALOG ITEM':
            if not self.marked_price_before:
                self.marked_price_before == self.catalog_item.marked_price

            if not self.selling_price_before:
                self.selling_price_before = self.catalog_item.selling_price

            if not self.threshold_price_before:
                self.threshold_price_before = self.catalog_item.threshold_price

            if not self.discount_amount_before:
                self.discount_amount_before = self.catalog_item.discount_amount

        if not self.marked_price_recorded:
            self.marked_price_recorded = self.catalog_item.marked_price

        if not self.marked_price_after:
            self.marked_price_after = self.marked_price_recorded or self.marked_price_before

        if not self.selling_price_recorded:
            self.selling_price_recorded = self.catalog_item.selling_price

        if not self.selling_price_after:
            self.selling_price_after = self.selling_price_recorded or self.selling_price_before

        if not self.threshold_price_recorded:
            self.threshold_price_recorded = self.catalog_item.threshold_price

        if not self.threshold_price_after:
            self.threshold_price_after = self.threshold_price_recorded or self.threshold_price_before   # noqa

        if not self.discount_amount_recorded:
            self.discount_amount_recorded = self.catalog_item.discount_amount or 0

        if not self.discount_amount_after:
            self.discount_amount_after = self.discount_amount_recorded or self.discount_amount_before   # noqa

    def validate_inventory_record_source_has_inventory_record_attached(self):
        """Validate inventory record source has an inventory record attached."""
        if self.audit_source == INVENTORY_RECORD and not self.inventory_record:
            msg = 'An audit coming from inventory records should have '\
                'the inventory record attached to it'
            raise ValidationError({'inventory_record': msg})

    def validate_closing_quantity(self):
        """Validate closing quantity."""
        expected_closing_quantity = self.quantity_before + self.quantity_recorded
        if not self.quantity_after == expected_closing_quantity:
            msg = 'The closing quantity is {} is not equal to '\
                'the expected closing quantity {}'.format(
                    self.quantity_after, expected_closing_quantity)
            raise ValidationError(
                {'closing_quantity': msg})

    def clean(self) -> None:
        """Clean catalog item."""
        self.validate_inventory_record_source_has_inventory_record_attached()
        self.validate_closing_quantity()
        return super().clean()

    def save(self, *args, **kwargs):
        """Catalog item model save."""
        self.get_quantity_after()
        self.get_amounts()
        if self.__class__.objects.filter(id=self.id).exists():
            self.audit_date = self.__class__.objects.filter(id=self.id).first().audit_date
        return super().save(*args, **kwargs)
