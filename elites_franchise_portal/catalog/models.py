"""Catalog model file."""

from decimal import Decimal
from django.db import models
from django.core.cache import cache
from django.core.exceptions import ValidationError

from elites_franchise_portal.common.choices import CURRENCY_CHOICES
from elites_franchise_portal.debit.models import InventoryItem
from elites_franchise_portal.items.models import ItemUnits, ItemAttribute
from elites_franchise_portal.common.models import AbstractBase
from elites_franchise_portal.common.validators import (
    items_elites_code_validator)
from elites_franchise_portal.customers.models import Customer
from django.contrib.auth import get_user_model
from elites_franchise_portal.users.models import retrieve_user_email
from elites_franchise_portal.common.code_generators import generate_elites_code
from django.core.validators import MinValueValidator

KSH = 'KSH'


class Section(AbstractBase):
    """Sections for items in the premise."""

    section_name = models.CharField(
        null=False, blank=False, max_length=250)
    section_code = models.CharField(
        max_length=250, null=True, blank=True, validators=[items_elites_code_validator])
    is_active = models.BooleanField(default=True)
    creator = retrieve_user_email('created_by')
    updater = retrieve_user_email('updated_by')

    def create_section_code(self):
        """Create section code."""
        if not self.section_code:
            self.section_code = generate_elites_code(self)

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
    is_active = models.BooleanField(default=False)
    pushed_to_edi = models.BooleanField(default=False)
    creator = retrieve_user_email('created_by')
    updater = retrieve_user_email('updated_by')

    def compose_item_heading(self):
        """Compose an item heading to display item."""
        type = self.inventory_item.item.item_model.brand_item_type.item_type.type_name
        brand = self.inventory_item.item.item_model.brand_item_type.brand.brand_name
        model = self.inventory_item.item.item_model.model_name
        units = ''

        if self.is_active:
            try:
                item_units = ItemUnits.objects.get(item=self.inventory_item.item)
                units = item_units.sales_units.units_name
            except ItemUnits.DoesNotExist:
                pass
                msg = 'Please assign units to {}'.format(
                    self.inventory_item.item.item_name)
                raise ValidationError({
                    'units': msg
                })

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
            self.selling_price = self.marked_price - self.discount_amount

    def get_threshold_price(self):
        """Get threshold price."""
        if not self.threshold_price:
            self.threshold_price = self.selling_price

    def add_to_cart(self, customer=None, price=None, quantity=None, is_installment=False, order_now=False): # noqa
        """Add item to cart."""
        from elites_franchise_portal.orders.models import Cart, CartItem
        if not customer:
            user = get_user_model().objects.get(id=self.updated_by)
            customer = Customer.objects.filter(franchise_user=user)
        cart = Cart.objects.filter(customer=customer)
        if not cart.exists():
            cart_data = {
                'created_by': self.created_by,
                'updated_by': self.updated_by,
                'franchise': self.franchise,
                'customer': customer,
            }
            Cart.objects.create(**cart_data)
        cart = Cart.objects.get(customer=customer, is_active=True)

        cart_item = CartItem.objects.filter(cart=cart, catalog_item=self, franchise=self.franchise)
        if price:
            if price < self.threshold_price:
                diff = float(self.threshold_price) - float(price)
                raise ValidationError(
                    {'price': f'The selling price is below the threshold price by {self.currency} {diff}'}) # noqa

        if not cart_item.exists():
            cart_item_data = {
                'created_by': self.created_by,
                'updated_by': self.updated_by,
                'franchise': self.franchise,
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

    def remove_from_cart(self):
        """Remove item from cart."""
        pass

    def clean(self) -> None:
        """Clean Catalog Item."""
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
        self.get_threshold_price()
        if not self.__class__.objects.filter(id=self.id).exists():
            # Pre save instance not created
            cache.delete('catalog_items_objects')
        super().save(*args, **kwargs)

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
    name = models.CharField(max_length=300, null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    is_standard_catalog = models.BooleanField(default=False)
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
            self.name,
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
