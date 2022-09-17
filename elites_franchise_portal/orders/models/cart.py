"""Order Cart models file."""

import random
import logging
from decimal import Decimal
from warnings import filters
from celery import shared_task

from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator

from elites_franchise_portal.common.models import AbstractBase
from elites_franchise_portal.catalog.models import CatalogItem
from elites_franchise_portal.customers.models import Customer
from elites_franchise_portal.encounters.models import Encounter

LOGGER = logging.getLogger(__name__)


class Cart(AbstractBase):
    """Cart model."""

    customer = models.ForeignKey(
        Customer, null=True, blank=True, on_delete=models.PROTECT)
    encounter = models.ForeignKey(
        Encounter, blank=True, null=True, on_delete=models.PROTECT)
    cart_code = models.CharField(
        null=True, blank=True, max_length=250)
    order_guid = models.UUIDField(null=True, blank=True)
    is_empty = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_checked_out = models.BooleanField(default=False)
    is_enterprise = models.BooleanField(default=False)

    # TODO set the is_empty flag as a property field

    @property
    def summary(self):
        """Summary of cart."""
        summarized_cart_items = []
        price_totals = []
        cart_items = CartItem.objects.filter(cart=self)

        if cart_items.exists():
            highest_cart_item = None
            ignore_cart_item_ids = []
            for cart_item in cart_items:
                if highest_cart_item:
                    if highest_cart_item.catalog_item == cart_item.catalog_item:
                        if cart_item.closing_quantity > highest_cart_item.closing_quantity:
                            highest_cart_item = cart_item
                        else:
                            ignore_cart_item_ids.append(cart_item.id)
                else:
                    highest_cart_item = cart_item

            cleaned_cart_items = CartItem.objects.filter(
                cart=self).exclude(id__in=ignore_cart_item_ids)
            for count, cleaned_cart_item in enumerate(cleaned_cart_items):
                price_totals.append(float(cleaned_cart_item.total_amount))
                summarized_cart_items.append(
                    {
                        'index': count,
                        'name': cleaned_cart_item.catalog_item.inventory_item.item.item_name,
                        'quantity': cleaned_cart_item.closing_quantity,
                        'price': float(cleaned_cart_item.selling_price),
                        'total': float(cleaned_cart_item.total_amount),
                    }
                )

        summary = {
            'items': summarized_cart_items,
            'grand_total': sum(price_totals)
        }

        return summary

    @property
    def order(self):
        from elites_franchise_portal.orders.models import Order
        order = None
        if self.order_guid:
            order = Order.objects.get(id=self.order_guid)
        
        return order

    def checkout_cart(self):
        """Checkout all items in cart."""
        cart_items = CartItem.objects.filter(cart=self, enterprise=self.enterprise)
        if not cart_items.exists():
            raise ValidationError({
                'cart item': 'Cart is empty. '
                'Please add items to checkout'
            })

        prices = []

        audit_fields = {
            'enterprise': self.enterprise,
            'created_by': self.created_by,
            'updated_by': self.updated_by,
        }

        from elites_franchise_portal.orders.models import (
            Order, InstantOrderItem, InstallmentsOrderItem)

        customer_orders = Order.objects.filter(
            customer=self.customer, is_cleared=False, is_active=True)

        if not customer_orders.exists():
            order = Order.objects.create(
                cart_code=self.cart_code, customer=self.customer, order_name="#{}".format(
                    self.enterprise),
                order_number='#{}'.format(random.randint(1001, 9999)), **audit_fields)

        else:
            update_data = {
                'is_enterprise': self.is_enterprise,
            }
            customer_orders.filter(cart_code=self.cart_code).update(**update_data)
            order = customer_orders.first()

        for cart_item in cart_items:
            quantity = cart_item.closing_quantity
            prices.append(float(cart_item.selling_price)*quantity)
            filters = {
                'order': order,
                'cart_item': cart_item,
            }
            payload = {
                'confirmation_status': 'PENDING',
                'quantity': quantity,
            }
            if cart_item.is_installment:
                installment_order_item = InstallmentsOrderItem.objects.filter(**filters)
                if installment_order_item.exists():
                    installment_order_item.update(**payload)
                else:
                    InstallmentsOrderItem.objects.create(**filters, **payload, **audit_fields)

            else:
                instant_order_item = InstantOrderItem.objects.filter(**filters)
                if instant_order_item.exists():
                    instant_order_item.update(**payload)
                else:
                    InstantOrderItem.objects.create(**filters, **payload, **audit_fields)

        self.__class__.objects.filter(id=self.id).update(order_guid=order.id, is_checked_out=True)

    def checkout_specific_items_in_cart(self, cart_items=[]):
        """Checkout a specific item in cart."""
        order_now_cart_items = CartItem.objects.filter(
            cart=self, enterprise=self.enterprise, order_now=True)
        if not cart_items and not order_now_cart_items:
            raise ValidationError({
                'cart item': 'Fast checkout cart is empty. '
                'Please add items to checkout'
            })

        for order_now_cart_item in order_now_cart_items:
            cart_items.append(order_now_cart_item)

        prices = []
        audit_fields = {
            'created_by': self.created_by,
            'updated_by': self.updated_by,
            'enterprise': self.enterprise,
        }
        from elites_franchise_portal.orders.models import (
            Order, InstantOrderItem, InstallmentsOrderItem)

        customer_orders = Order.objects.filter(
            customer=self.customer, is_cleared=False, is_active=True)

        if not customer_orders.exists():
            order = Order.objects.create(
                order_name="#{}".format(self.enterprise), cart_code=self.cart_code,
                order_number='#{}'.format(random.randint(1001, 9999)),
                customer=self.customer, **audit_fields)

        else:
            update_data = {
                'is_enterprise': self.is_enterprise,
                'customer': Customer.objects.get(id=self.updated_by)
            }
            customer_orders.filter(cart_code=self.cart_code).update(**update_data)
            order = customer_orders.first()

        for cart_item in cart_items:
            quantity = cart_item.closing_quantity
            prices.append(float(cart_item.selling_price)*quantity)

            if cart_item.is_installment:
                # create an installment order item
                InstallmentsOrderItem.objects.get_or_create(
                    order=order, cart_item=cart_item, confirmation_status='PENDING',
                    quantity=quantity, **audit_fields)

            else:
                # create an instant order item
                InstantOrderItem.objects.get_or_create(
                    order=order, cart_item=cart_item, confirmation_status='PENDING',
                    quantity=quantity, **audit_fields)

    def check_if_on_site_cart(self):
        """Check if item is being processed under the company's default customers."""
        if self.customer and self.customer.is_enterprise:
            self.is_enterprise = True

    def validate_one_empty_active_cart_per_customer(self):
        """Validate one active cart per customer."""
        carts = self.__class__.objects.filter(
            encounter=self.encounter, customer=self.customer, is_active=True,
            is_checked_out=False, is_empty=True)
        if carts.exists() and not carts.filter(id=self.id).exists():
            raise ValidationError(
                {'active_cart': 'The customer already has an active empty cart'})

    def clean(self) -> None:
        """Clean Cart."""
        self.validate_one_empty_active_cart_per_customer()
        return super().clean()

    def __str__(self):
        """Str representation for the item-models model."""
        return '{} -> {}'.format(self.customer.full_name, self.cart_code)

    def save(self, *args, **kwargs):
        """Perform pre save and post save actions."""
        if not self.cart_code:
            self.cart_code ='#{}'.format(random.randint(1001, 9999))
        self.check_if_on_site_cart()
        super().save(*args, **kwargs)

    class Meta:
        """Meta class for cart model."""

        ordering = ['-created_on', ]


class CartItem(AbstractBase):
    """Cart Item model."""

    cart = models.ForeignKey(Cart, null=False, blank=False, on_delete=models.PROTECT)
    catalog_item = models.ForeignKey(
        CatalogItem, null=False, blank=False, on_delete=models.PROTECT)
    opening_quantity = models.FloatField(null=True, blank=True, default=0)
    quantity_added = models.FloatField(null=False, blank=False, default=0)
    closing_quantity = models.FloatField(null=True, blank=True, default=0)
    selling_price = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=True, blank=True)
    total_amount = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=True, blank=True, default=0)
    is_installment = models.BooleanField(default=False)
    order_now = models.BooleanField(default=False)

    def get_opening_and_closing_quantity(self):
        """Calculate opening and closing quantities."""
        opening_quantity = 0
        cart_items = self.__class__.objects.filter(
            cart=self.cart, catalog_item=self.catalog_item,
            enterprise=self.enterprise).order_by('-closing_quantity')

        if cart_items.exists():
            for cart_item in cart_items:
                if cart_item.closing_quantity >= opening_quantity:
                    opening_quantity = cart_item.closing_quantity

        self.opening_quantity = opening_quantity
        self.closing_quantity = self.opening_quantity + self.quantity_added

    def get_selling_price(self):
        """Get the selling price."""
        if not self.selling_price:
            self.selling_price = Decimal(self.catalog_item.selling_price)

    def get_total_amount(self):
        """Get the total of the cart item."""
        total = float(self.selling_price) * self.closing_quantity
        self.total_amount = total

    def activate_installments(self):
        """Hitting this function will set is_installment to True(LipaMdogoMdogo)."""
        cart_item = self.__class__.objects.get(id=self.id)
        cart_item.is_installment = True
        cart_item.save()
        # TODO remove items from Instant and move them to installment order items

    def checkout_cart_item(self):
        """Complete order for a select item."""
        from elites_franchise_portal.orders.models import (
            Order, InstantOrderItem, InstallmentsOrderItem)
        # create order
        # create order item
        # prices = []
        audit_fields = {
            'enterprise': self.enterprise,
            'created_by': self.created_by,
            'updated_by': self.updated_by,
        }

        quantity = self.closing_quantity
        item_name = self.catalog_item.inventory_item.item.item_name

        order = Order.objects.create(
            order_name="#{}".format(self.enterprise),
            order_number='#{}'.format(random.randint(1001, 9999)),
            customer=self.cart.customer, **audit_fields)

        if self.is_installment:
            # log info this
            total = float(self.selling_price) * quantity
            InstallmentsOrderItem.objects.get_or_create(
                order=order, cart_item=self, confirmation_status='PENDING', total_amount=total,
                quantity_awaiting_clearance=quantity, quantity=quantity, **audit_fields)
            msg = 'Created an installment order item for {} as a single cart item'.format(
                item_name)
            LOGGER.info(f'{msg}')

        else:
            total = float(self.selling_price) * quantity
            InstantOrderItem.objects.get_or_create(
                order=order, cart_item=self, confirmation_status='PENDING', total_amount=total,
                quantity_awaiting_clearance=quantity, quantity=quantity, **audit_fields)
            msg = 'Created an instant order item for {} as a single cart item'.format(item_name)
            LOGGER.info(f'{msg}')

    def clean(self) -> None:
        """Clean Cart Item."""
        return super().clean()

    def save(self, *args, **kwargs):
        """Perform pre save and post save actions."""
        self.get_opening_and_closing_quantity()
        self.get_selling_price()
        self.get_total_amount()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        """Represent cart item in string format."""
        item_name = f'{self.catalog_item.inventory_item.item.item_name}'
        return item_name

    class Meta:
        """Meta class for Cart Item."""

        ordering = ['-closing_quantity', 'catalog_item__inventory_item__item__item_name']
