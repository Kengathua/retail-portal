"""Catalog model file."""

from decimal import Decimal
from django.db import models
from django.core.cache import cache
from django.core.exceptions import ValidationError

from elites_franchise_portal.common.choices import CURRENCY_CHOICES
from elites_franchise_portal.debit.models import (
    Inventory, InventoryItem, InventoryRecord)
from elites_franchise_portal.items.models import ItemUnits, ItemAttribute
from elites_franchise_portal.common.models import AbstractBase
from elites_franchise_portal.common.validators import (
    items_enterprise_code_validator)
from elites_franchise_portal.customers.models import Customer
from django.contrib.auth import get_user_model
from elites_franchise_portal.users.models import retrieve_user_email
from elites_franchise_portal.common.code_generators import (
    generate_enterprise_code)
from django.core.validators import MinValueValidator

KSH = 'KSH'

AUDIT_RECORD_TYPE_CHOICES = (
    ('ADD', 'ADD'),
    ('REMOVE', 'REMOVE')
)

AUDIT_OPERATIONS_TYPE_CHOICES = (
    ('CREATE', 'CREATE'),
    ('UPDATE', 'CREATE'),
)

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
        # validate_franchise_exists(self)
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

    def compose_item_heading(self):
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
            special_offer = ' + {}'.format(str_special_offers)

        str_special_features = ''
        if special_features:
            str_special_features = ", ".join(special_features)

        item_heading = brand + ' ' + model + ' ' + \
            str_special_features + ' ' + type + ', ' + \
            year + units + special_offer

        self.item_heading = item_heading

    def get_marked_price(self):
        """Get marked price."""
        if not self.marked_price:
            self.marked_price = Decimal(self.inventory_item.unit_price)

    def get_selling_price(self):
        """Initialize the selling price."""
        if not self.selling_price:
            self.selling_price = Decimal(
                float(self.marked_price) - float(self.discount_amount))

    def get_threshold_price(self):
        """Get threshold price."""
        if not self.threshold_price:
            self.threshold_price = self.selling_price

    def get_quantity(self):
        """Get quantity."""
        from elites_franchise_portal.enterprise_mgt.helpers import (
            get_valid_enterprise_setup_rules)
        inventories = Inventory.objects.filter(is_active=True, enterprise=self.enterprise)

        if inventories.exists() and not inventories.filter(is_master=True).exists():
            raise ValidationError(
                {'inventory':
                    'Your enterprise does not have a master Inventory. Please set up one first'})

        if not self.quantity:
            quantity = 0
            enterprise_setup_rules = get_valid_enterprise_setup_rules(self.enterprise)
            available_inventory = enterprise_setup_rules.available_inventory
            if not available_inventory.summary == []:
                quantities = [
                    data['quantity'] for data in available_inventory.summary
                    if data['inventory_item'] == self.inventory_item]

                quantity = quantities[0] if quantities else 0

            self.quantity = quantity

    def add_to_cart(
            self, customer=None, price=None,
            quantity=None, is_installment=False, order_now=False):
        """Add item to cart."""
        from elites_franchise_portal.orders.models import Cart, CartItem
        if not customer:
            user = get_user_model().objects.get(id=self.updated_by)
            customer = Customer.objects.filter(enterprise_user=user)
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
            cart=cart, catalog_item=self, enterprise=self.enterprise)
        if price:
            if price < self.threshold_price:
                diff = float(self.threshold_price) - float(price)
                raise ValidationError(
                    {'price': f'The selling price is below the threshold price by {self.currency} {diff}'}) # noqa

        if not cart_item.exists():
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

        cart_item = cart_item.first()
        cart_item.quantity_added = 1 if not quantity else quantity
        cart_item.is_installment = is_installment
        cart_item.order_now = order_now
        cart_item.save()
        return cart_item

    def validate_item_is_active(self):
        """Remove item from cart."""
        if self.is_active:
            item_units = ItemUnits.objects.filter(item=self.inventory_item.item)
            if not item_units.exists():
                msg = 'Please assign units to {}'.format(
                    self.inventory_item.item.item_name)

                raise ValidationError(
                    {'item_units': msg})

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
        self.compose_item_heading()
        self.get_marked_price()
        self.get_selling_price()
        self.get_quantity()
        self.get_threshold_price()
        super().save(*args, **kwargs)

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
    deactivated_on = models.DateTimeField(null=True, blank=True)
    deactivation_reason = models.TextField(null=True, blank=True)
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
    quantity_before = models.FloatField(default=0)
    quantity_recorded = models.FloatField(default=0)
    quantity_after = models.FloatField(default=0)
    selling_price_before = models.FloatField(default=0)
    selling_price_recorded = models.FloatField(default=0)
    selling_price_after = models.FloatField(default=0)
    marked_price_before = models.FloatField(default=0)
    marked_price_recorded = models.FloatField(default=0)
    marked_price_after = models.FloatField(default=0)
    threshold_price_before = models.FloatField(default=0)
    threshold_price_recorded = models.FloatField(default=0)
    threshold_price_after = models.FloatField(default=0)
    discount_amount_before = models.FloatField(default=0)
    discount_amount_recorded = models.FloatField(default=0)
    discount_amount_after = models.FloatField(default=0)
    record_type = models.CharField(max_length=300, choices=AUDIT_RECORD_TYPE_CHOICES)
    operation_type = models.CharField(max_length=300, choices=AUDIT_OPERATIONS_TYPE_CHOICES)
    inventory_record = models.ForeignKey(InventoryRecord, on_delete=models.PROTECT)

    def get_quantity_before(self):
        if not self.quantity_before:
            self.quantity_before = 0
            previous_logs = self.__class__.objects.filter(catalog_item=self.catalog_item).exclude(id=self.id)
            if previous_logs.exists():
                inventory_record_logs = previous_logs.filter(inventory_record=self.inventory_record)
                if inventory_record_logs.exists():
                    latest_log = inventory_record_logs.latest('created_on')
                    self.quantity_before = latest_log.quantity_after
                    if self.operation_type == 'UPDATE':
                        self.quantity_before = latest_log.quantity_before
                        if latest_log.quantity_recorded != self.quantity_recorded:
                            diff = self.quantity_recorded - latest_log.quantity_recorded
                            self.quantity_before = previous_logs.latest('inventory_record__created_on').quantity_after
                            self.quantity_recorded = diff
                            self.quantity_after = self.quantity_before + self.quantity_recorded

                else:
                    self.quantity_before = previous_logs.latest('created_on').quantity_after


    def get_quantity_after(self):
        if not self.quantity_after:
            self.quantity_after = self.quantity_before + self.quantity_recorded

    def validate_quantity_after(self):
        expected_closing_quantity = self.quantity_before + self.quantity_recorded
        if not self.quantity_after == expected_closing_quantity:
            msg = 'The closing quantity is {} is not equal to '\
                'the expected closing quantity {}'.format(
                    self.quantity_after, expected_closing_quantity)
            raise ValidationError(
                {'closing_quantity': msg})

    def clean(self) -> None:
        self.validate_quantity_after()
        return super().clean()

    def save(self, *args, **kwargs):
        self.get_quantity_before()
        self.get_quantity_after()
        return super().save(*args, **kwargs)
