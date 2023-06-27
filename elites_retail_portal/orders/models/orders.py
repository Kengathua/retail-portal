"""Orders models file."""
import logging

from decimal import Decimal
from datetime import timedelta, date

from django.db import models
from django.db.models import PROTECT, CASCADE
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator

from elites_retail_portal.common.models import AbstractBase
from elites_retail_portal.orders.models import CartItem, Cart

from elites_retail_portal.customers.models import Customer
from elites_retail_portal.transactions.models import Transaction, Payment
from elites_retail_portal.users.models import retrieve_user_email

LOGGER = logging.getLogger(__name__)

ORDER_CONFIRMATION_STATUS_CHOICES = (
    ('PENDING', 'PENDING'),
    ('CONFIRMED', 'CONFIRMED'),
    ('CANCELED', 'CANCELED'),
)

PAYMENT_STATUS_CHOICES = (
    ('NOT PAID', 'NOT PAID'),
    ('DEPOSIT PAID', 'DEPOSIT PAID'),
    ('DEPOSIT PARTIALLY PAID', 'DEPOSIT PARTIALLY PAID'),
    ('PARTIALLY PAID', 'PARTIALLY PAID'),
    ('FULLY PAID', 'FULLY PAID'),
    ('NOT PAID AND RETURNED', 'NOT PAID AND RETURNED'),
    ('PARTIALLY PAID AND RETURNED', 'PARTIALLY PAID AND RETURNED'),
)

TRANSACTION_STATUS_CHOICES = (
    ('FAILED', 'FAILED'),
    ('PENDING', 'PENDING'),
    ('ONGOING', 'ONGOING'),
    ('SUCCESS', 'SUCCESS'),
    ('STALLED', 'STALLED'),
    ('CANCELED', 'CANCELED'),
    ('RECEIVED', 'RECEIVED'),
)

ITEM_PAYMENT_TYPES = (
    ('INSTANT', 'INSTANT'),
    ('INSTALLMENTS', 'INSTALLMENTS')
)

ITEM_PAYMENT_PLANS = (
    ('DAILY', 'DAILY'),
    ('2 DAYS', '2 DAYS'),
    ('WEEKLY', 'WEEKLY'),
    ('2 WEEKS', '2 WEEKS'),
    ('MONTHLY', 'MONTHLY')
)

INSTALLMENT_ITEM_PREFERENCE_LEVELS = (
    ('LOW', 'LOW'),
    ('EQUAL', 'EQUAL'),
    ('NORMAL', 'NORMAL'),
    ('MODERATE', 'MODERATE'),
    ('HIGH', 'HIGH'),
    ('VERY HIGH', 'VERY HIGH'),
)

INSTALLMENT_ITEM_PREFERENCE_TYPES = (
    ('FLAT', 'FLAT'),
    ('PERCENTAGE', 'PERCENTAGE'),
    ('RATIO', 'RATIO'),
)

STATUS_CHOICES = (
    ('FAILED', 'FAILED'),
    ('PENDING', 'PENDING'),
    ('ONGOING', 'ONGOING'),
    ('SUCCESS', 'SUCCESS'),
    ('STALLED', 'STALLED'),
    ('CANCELED', 'CANCELED'),
)

NOT_PAID = 'NOT PAID'
DEPOSIT_PAID = 'DEPOSIT PAID'
DEPOSIT_PARTIALLY_PAID = 'DEPOSIT PARTIALLY PAID'
PARTIALLY_PAID = 'PARTIALLY PAID'
FULLY_PAID = 'FULLY PAID'
PENDING = 'PENDING'
INSTANT = 'INSTANT'
MONTHLY = 'MONTHLY'
NORMAL = 'NORMAL'
RATIO = 'RATIO'

now = timezone.now()


class Order(AbstractBase):
    """Order Model."""

    customer = models.ForeignKey(
        Customer, null=True, blank=True, on_delete=models.PROTECT)
    cart_code = models.CharField(null=True, blank=True, max_length=300)
    order_number = models.CharField(null=True, blank=True, max_length=250)
    order_name = models.CharField(null=True, blank=True, max_length=300)
    order_date = models.DateTimeField(
        db_index=True, editable=False, default=timezone.now)
    instant_order_items_total = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=True, blank=True, default=0)
    installment_order_items_total = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=True, blank=True, default=0)
    order_total = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=True, blank=True, default=0)
    is_processed = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_cleared = models.BooleanField(default=False)
    is_site = models.BooleanField(default=False)
    status = models.CharField(max_length=300, choices=STATUS_CHOICES, default=PENDING)

    def compose_order_name(self):
        """Compose order name."""
        order_name = f'{self.order_number}'
        instant_order_items = InstantOrderItem.objects.filter(order__id=self.id)
        installment_order_items = InstallmentsOrderItem.objects.filter(order__id=self.id)
        names = []
        if instant_order_items:
            for instant_order_item in instant_order_items:
                names.append(
                    instant_order_item.cart_item.catalog_item.inventory_item.item.item_name)

        if installment_order_items:
            for installment_order_item in installment_order_items:
                names.append(
                    installment_order_item.cart_item.catalog_item.inventory_item.item.item_name)    # noqa

        item_names = ', '.join(names)

        return "{} {}".format(order_name, item_names)

    @property
    def heading(self):
        """Order heading."""
        return self.compose_order_name()

    @property
    def summary(self):
        """Generate Order Summary."""
        instant_order_items = InstantOrderItem.objects.filter(order=self)
        installment_order_items = InstallmentsOrderItem.objects.filter(order=self)
        order_total = 0
        instant_item_spending = []
        installment_item_spending = []
        amount_paid_total = 0
        order_total = 0
        if instant_order_items.exists():
            for instant_order_item in instant_order_items:
                total_amount = instant_order_item.total_amount
                amount_paid = instant_order_item.amount_paid
                amount_paid_total += amount_paid
                order_total += total_amount

                data = {
                    'item': instant_order_item,
                    'total_amount': total_amount,
                    'amount_paid': amount_paid,
                }
                instant_item_spending.append(data)

        if installment_order_items.exists():
            for installment_order_item in installment_order_items:
                total_amount = installment_order_item.total_amount
                amount_paid = installment_order_item.amount_paid
                amount_paid_total += amount_paid
                order_total += total_amount

                data = {
                    'item': installment_order_item,
                    'total_amount': total_amount,
                    'amount_paid': amount_paid,
                }
                installment_item_spending.append(data)

        amount_due = order_total - amount_paid_total
        summary = {
            'paid_total': amount_paid_total,
            'amount_due': amount_due,
            'order_total': order_total,
            'instant_items': instant_item_spending,
            'installment_items': installment_item_spending,
            }

        return summary

    @property
    def payments(self):
        """Get all payments attached to the order."""
        return Payment.objects.filter(encounter__order_guid=self.id)

    def process_order(self):
        """Process order."""
        order = self.__class__.objects.get(id=self.id, order_number=self.order_number)
        instant_order_items = InstantOrderItem.objects.filter(order=order)
        installment_order_items = InstallmentsOrderItem.objects.filter(
            order=order)

        if not instant_order_items.exists() and not installment_order_items.exists():
            msg = 'The order is empty. Please add an item to cart and complete your order.'
            raise ValidationError({
                'order': msg
            })

        self.__class__.objects.filter(id=order.id).update(is_processed=True)
        cart = Cart.objects.filter(cart_code=self.cart_code, enterprise=self.enterprise)
        if cart.exists():
            cart = cart.first()
            cart.is_active = True
            cart.save()

        # send email and sms notification to user

    def get_order_total(self):
        """Get order total."""
        instant_order_items_total = 0
        installment_order_items_total = 0
        order_total = 0
        instant_items = InstantOrderItem.objects.filter(order=self)
        if instant_items.exists():
            prices = []
            for item in instant_items:
                price = float(item.cart_item.selling_price)
                total_price = price * item.cart_item.closing_quantity
                prices.append(total_price)

            instant_order_items_total = sum(prices)

        installment_items = InstallmentsOrderItem.objects.filter(order=self)
        if installment_items.exists():
            prices = []
            for item in installment_items:
                price = float(item.cart_item.selling_price)
                total_price = price * item.cart_item.closing_quantity
                prices.append(total_price)

            installment_order_items_total = sum(prices)

        order_total = instant_order_items_total + installment_order_items_total
        self.instant_order_items_total = instant_order_items_total
        self.installment_order_items_total = installment_order_items_total
        self.order_total = order_total

    def clean(self) -> None:
        """Clean order."""
        super().clean()

    def __str__(self) -> str:
        """Represent an order in string format."""
        order_representation = f'{self.customer.full_name} {self.order_name} {self.order_number}'
        return order_representation

    def save(self, *args, **kwargs):
        """Perform pre save and post save."""
        from elites_retail_portal.debit.models import Sale
        self.order_name = self.compose_order_name()
        self.get_order_total()
        super().save(*args, **kwargs)
        order = self.__class__.objects.filter(id=self.id).first()
        sales = Sale.objects.filter(order=order)
        if order:
            if not sales.exists():
                audit_fields = {
                    'created_by': self.created_by,
                    'updated_by': self.updated_by,
                    'enterprise': self.enterprise,
                }

                Sale.objects.create(
                    order=order, customer=self.customer, **audit_fields)

            order.refresh_from_db()
            if order.is_cleared:
                sale = sales.first()
                sale.is_cleared = True
                sale.save()

    class Meta:
        """Meta class for order model."""

        ordering = ['-created_on', ]


class AbstractOrderItem(AbstractBase):
    """Abstract class for order items."""

    order = models.ForeignKey(
        Order, null=False, blank=False, on_delete=PROTECT)
    cart_item = models.ForeignKey(
        CartItem, null=False, blank=False, on_delete=PROTECT)
    quantity = models.FloatField(default=0)
    unit_price = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=True, blank=True, default=0)
    confirmation_status = models.CharField(
        null=False, blank=False, max_length=250,
        choices=ORDER_CONFIRMATION_STATUS_CHOICES, default=PENDING)
    total_amount = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=True, blank=True, default=0)
    amount_paid = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=True, blank=True, default=0)
    amount_due = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=True, blank=True, default=0)
    payment_is_processed = models.BooleanField(default=False)
    payment_status = models.CharField(
        max_length=250, choices=PAYMENT_STATUS_CHOICES, default=NOT_PAID)
    quantity_cleared = models.IntegerField(default=0)
    quantity_awaiting_clearance = models.IntegerField(default=0)
    quantity_returned = models.IntegerField(default=0)
    is_cleared = models.BooleanField(default=False)
    is_canceled = models.BooleanField(default=False)
    status = models.CharField(max_length=300, choices=STATUS_CHOICES, default=PENDING)

    @property
    def customer(self):
        """Get the customer."""
        return self.order.customer

    def get_unit_price(self):
        """Get the price per item."""
        if not self.unit_price:
            quantity = self.quantity if self.quantity else 1
            self.unit_price = float(self.total_amount) / quantity

    def validate_item_exists_in_inventory_or_cleared_from_store(self):
        """Validate that item exists in catalog, inventory and store."""
        from elites_retail_portal.catalog.helpers import (
            get_catalog_item_available_quantity)
        catalog_item = self.cart_item.catalog_item
        if self.is_cleared:
            available_quantity = get_catalog_item_available_quantity(catalog_item, False)
            if self.quantity > available_quantity:
                msg = 'There are not enough items in the catalog to fulfil this order'
                raise ValidationError(
                    {'quantity': msg})

    def validate_quantity_cleared_less_than_or_equal_to_quantity(self):
        """Validate quantity cleared is less than or equak to quantity."""
        if not self.quantity_cleared <= self.quantity:
            raise ValidationError(
                {'quantity': 'The number of items cleared {} '
                    'cannot be more than the ordered quantity {}'.format(
                        self.quantity_cleared, int(self.quantity))})

    def get_total_amount(self):
        """Get total for the order item."""
        self.total_amount = Decimal(float(self.cart_item.selling_price) * self.quantity)   # noqa

    def get_quantity(self):
        """Get the quantity being ordered."""
        if not self.quantity:
            self.quantity = self.cart_item.closing_quantity

    def get_quantity_awaiting_clearance(self):
        """Get the number of items awaiing clearance."""
        self.quantity_awaiting_clearance = self.quantity - self.quantity_cleared

    def clean(self) -> None:
        """Clean Order Item."""
        self.validate_item_exists_in_inventory_or_cleared_from_store()
        self.validate_quantity_cleared_less_than_or_equal_to_quantity()
        return super().clean()

    def save(self, *args, **kwargs):
        """Perform pre save and post save actions."""
        self.get_unit_price()
        self.get_quantity()
        self.get_total_amount()
        self.get_quantity_awaiting_clearance()
        super().save(*args, **kwargs)
        from elites_retail_portal.debit.models import Sale, SaleItem
        self.order.refresh_from_db()
        sale = Sale.objects.filter(order=self.order).first()
        if self.is_cleared:
            audit_fields = {
                'created_by': self.created_by,
                'updated_by': self.updated_by,
                'enterprise': self.enterprise
                }
            filters = {
                'sale': sale,
                'catalog_item': self.cart_item.catalog_item,
            }
            sale_item_payload = {
                'product': self.cart_item.product,
                'quantity_sold': self.quantity,
                'sale_type': 'INSTANT' if self.__class__.__name__ == 'InstantOrderItem' else 'INSTALLMENT',  # noqa
                'selling_price': self.unit_price,
                'amount_paid': self.amount_paid,
                'is_cleared': self.is_cleared,
                'processing_status': "PROCESSED" if self.is_cleared else "PENDING"
            }
            sale_item = SaleItem.objects.filter(**filters)

            if self.cart_item.product:
                self.cart_item.product.status = 'SOLD'
                self.cart_item.product.save()

            if sale_item.exists():
                sale_item.update(updated_by=self.updated_by, **sale_item_payload)
            else:
                SaleItem.objects.create(**filters, **sale_item_payload, **audit_fields)
            self.__class__.objects.filter(id=self.id).update(status="SUCCESS")

    class Meta:
        """Meta class for order items."""

        abstract = True
        ordering = [
            '-cart_item__catalog_item__inventory_item__item__item_name', '-total_amount']

    # TODO Assert the totals generated (
        # from cart selling price) are correct for different instances
    # USE cart unit price, inventory item unit price


class InstantOrderItem(AbstractOrderItem):
    """Instant Order Item model."""

    def save(self, *args, **kwargs):
        """Perform pre save and post save actions."""
        super().save(*args, **kwargs)

    class Meta(AbstractOrderItem.Meta):
        """Meta class for instant order items."""

    ordering = ['-total']


class InstallmentsOrderItem(AbstractOrderItem):
    """Installement order item model."""

    total_installments = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=True, blank=True, default=0)
    deposit_amount = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=True, blank=True, default=0)
    payment_plan = models.CharField(
        null=False, blank=False, max_length=250, choices=ITEM_PAYMENT_PLANS, default=MONTHLY)
    start_date = models.DateField(
        null=False, blank=False, default=date.today)
    speculated_end_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    preference_level = models.CharField(
        max_length=300, choices=INSTALLMENT_ITEM_PREFERENCE_LEVELS, default=NORMAL)
    preference_type = models.CharField(
        max_length=300, choices=INSTALLMENT_ITEM_PREFERENCE_TYPES, default=RATIO)
    share_value = models.FloatField(null=True, blank=True, default=1)
    quantity_on_full_deposit = models.IntegerField(default=0)
    quantity_on_partial_deposit = models.IntegerField(default=0)
    quantity_without_deposit = models.IntegerField(null=True, blank=True)

    def get_minimum_deposit(self):
        """Get minimum allowable deposit for an installment order item."""
        item_total = float(self.cart_item.selling_price) * self.quantity
        minimum_deposit = 0.2 * item_total

        installment_items = self.__class__.objects.filter(order=self.order)
        share_ratio = 1
        installment_items_selling_prices = []
        if installment_items.exists():
            installment_items_selling_prices.append(item_total)
            for installment_item in installment_items:
                if installment_item != self:
                    price = float(installment_item.total_amount)
                    installment_items_selling_prices.append(price)

            total_installment_items_selling_prices = sum(installment_items_selling_prices)
            if total_installment_items_selling_prices != 0:
                share_ratio = item_total/total_installment_items_selling_prices

        if InstantOrderItem.objects.filter(order=self.order).exists():
            instant_order_items = InstantOrderItem.objects.filter(
                order=self.order)
            instant_items_total_price = 0
            for instant_order_item in instant_order_items:
                instant_items_total_price += instant_order_item.total_amount

            instant_item_total_share_price = share_ratio * float(instant_items_total_price)
            minimum_deposit -= float(instant_item_total_share_price)

            if minimum_deposit < 0:
                minimum_deposit = 0

        return minimum_deposit

    @property
    def minimum_deposit(self):
        """Get minimu deposit based on a 20% of order fee."""
        minimum_deposit = self.get_minimum_deposit()
        return minimum_deposit

    def initialize_deposit(self):
        """Initialize deposit."""
        if self.deposit_amount == 0 and self.amount_paid > 0 and self.amount_paid < self.total_amount:  # noqa
            self.deposit_amount = self.minimum_deposit

    def get_quantity_without_deposit(self):
        """Initialize the number of items that do not have a deposit."""
        if not self.quantity_without_deposit:
            self.quantity_without_deposit = self.quantity

        if self.quantity_on_partial_deposit:
            self.quantity_without_deposit = self.quantity - self.quantity_on_partial_deposit

        if self.quantity_on_full_deposit:
            self.quantity_without_deposit = self.quantity - self.quantity_on_full_deposit

    def calculate_speculated_end_date(self):
        """Calculate the speculated end date of paying installements based on a 3 months rule"""    # noqa
        if self.start_date:
            self.speculated_end_date = self.start_date + timedelta(90)

    def validate_deposit_more_than_minimum_deposit(self):
        """Validate that the deposit is above the minimum deposit."""
        if self.deposit_amount:
            if self.deposit_amount < self.minimum_deposit and self.minimum_deposit > 0:
                raise ValidationError({
                    'deposit':
                    'Your deposit of KSH {} is too low. The minimum deposit for this order is KSH {}'.format(self.deposit_amount, self.minimum_deposit) # noqa
                })

    def get_amount_paid(self):
        """Calculate the amount paid."""
        self.amount_paid = Decimal(self.total_installments) + Decimal(self.deposit_amount)

    def get_amount_due(self):
        """Calculate amount due."""
        amount_due = 0
        if float(self.amount_paid) < float(self.total_amount):
            selling_price = float(self.cart_item.selling_price)
            total_cost = self.quantity * selling_price
            assert Decimal(total_cost) == self.total_amount
            amount_due = Decimal(total_cost) - Decimal(self.amount_paid)

        self.amount_due = amount_due

    def clear_installment_item(self):
        """Clear an installement item."""
        installment_item = self.__class__.objects.filter(id=self.id)
        if installment_item.exists():
            if self.amount_paid >= self.total_amount and self.quantity > 0:
                installment_item.update(is_cleared=True)

    def get_share_value(self):
        """Get the share value of the item to amounts added (deposit and installments)."""
        SHARE_VALUE_DEFAULT_MAPPER = {  # noqa
            'LOW': 20,
            'MODERATE': 40,
            'HIGH': 60,
            'VEY HIGH': 80,
        }
        installment_order_items = self.__class__.objects.filter(order=self.order)
        installment_order_items_total_amounts = installment_order_items.values_list(
            'total_amount', flat=True)
        if installment_order_items_total_amounts.exists():
            installment_order_items_total_amount = sum(installment_order_items_total_amounts)
            if self.preference_level == NORMAL and self.preference_type == RATIO:
                ratio = self.total_amount / installment_order_items_total_amount if self.total_amount and installment_order_items_total_amount else 1   # noqa
                self.share_value = ratio

            if self.preference_level == 'EQUAL':
                no_of_installment_items = sum(
                    installment_order_items.values_list('quantity', flat=True))
                ratio = self.quantity / no_of_installment_items
                self.share_value = ratio

    def clean(self) -> None:
        """Clean Installment order item."""
        self.validate_deposit_more_than_minimum_deposit()
        return super().clean()

    def save(self, *args, **kwargs):
        """Perform pre save and post save actions."""
        self.get_quantity()
        self.initialize_deposit()
        self.calculate_speculated_end_date()
        self.get_quantity_without_deposit()
        self.get_total_amount()
        self.get_amount_paid()
        self.get_amount_due()
        self.get_share_value()
        super().save(*args, **kwargs)
        self.clear_installment_item()


def create_order_transaction_code():
    """."""
    id = '#EAG-T-0001'
    return id


def create_order_transaction_name():
    """."""
    name = 'Transaction1'
    return name


class OrderTransaction(AbstractBase):
    """Order Transaction model."""

    order = models.ForeignKey(
        Order, null=False, blank=False, on_delete=models.PROTECT)
    transaction = models.ForeignKey(
        Transaction, null=False, blank=False, on_delete=models.PROTECT)
    order_transaction_code = models.CharField(
        null=False, blank=False, max_length=300,
        default=create_order_transaction_code)
    order_transaction_name = models.CharField(
        null=False, blank=False, max_length=300,
        default=create_order_transaction_name)
    amount = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=True, blank=True, default=0)
    balance = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=True, blank=True)
    is_processed = models.BooleanField(default=False)
    is_installment = models.BooleanField(default=False)
    status = models.CharField(
        max_length=300, choices=TRANSACTION_STATUS_CHOICES, default=PENDING)

    def initialize_balance(self):
        """Initialize Balance."""
        if not self.balance and not self.is_processed:
            self.balance = self.amount

    def clean(self) -> None:
        """Clean Order Transaction model."""
        self.initialize_balance()
        return super().clean()

    def process_order_clearance(self):
        """Process order clearance."""
        instant_order_items = InstantOrderItem.objects.filter(order=self.order)
        installment_order_items = InstallmentsOrderItem.objects.filter(order=self.order)
        instant_order_items_cleared = True
        installment_order_items_cleared = True
        if instant_order_items.exists():
            for instant_order_item in instant_order_items:
                if not instant_order_item.is_cleared:
                    instant_order_items_cleared = False

        if installment_order_items.exists():
            for installment_order_item in installment_order_items:
                if not installment_order_item.is_cleared:
                    installment_order_items_cleared = False

        if instant_order_items_cleared and installment_order_items_cleared:
            order = self.order
            order.is_cleared = True
            order.save()

    def save(self, *args, **kwargs):
        """Perform pre save and post save actions."""
        super().save(*args, **kwargs)
        # self.process_order_clearance()

    class Meta:
        """Meta class for order transactions."""

        ordering = ['-order']


class OrderStatusLog(AbstractBase):
    """Order status log model."""

    order = models.ForeignKey(
        Order, null=False, blank=False, on_delete=PROTECT)
    status_from = models.CharField(
        null=False, blank=False, max_length=250,
        choices=ORDER_CONFIRMATION_STATUS_CHOICES)
    status_to = models.CharField(
        null=False, blank=False, max_length=250,
        choices=ORDER_CONFIRMATION_STATUS_CHOICES)
    transition_date = models.DateTimeField(default=timezone.now)
    creator = retrieve_user_email('created_by')
    updater = retrieve_user_email('updated_by')


class Installment(AbstractBase):
    """Installment model."""

    installment_code = models.CharField(null=True, blank=True, max_length=300)
    order_transaction = models.ForeignKey(
        OrderTransaction, null=False, blank=False, on_delete=models.CASCADE)
    installment_item = models.ForeignKey(
        InstallmentsOrderItem, null=True, blank=True, on_delete=CASCADE)
    amount = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=False, blank=False)
    balance = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=True, blank=True)
    installment_date = models.DateTimeField(db_index=True, default=timezone.now)
    next_installment_date = models.DateField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    is_direct_installment = models.BooleanField(default=False)

    @property
    def previous_installment_date(self):
        """Calculate the next installment date."""
        previous_installments = self.__class__.objects.filter(
            installment_item=self.installment_item, installment_date__lt=self.installment_date)
        if not previous_installments.exists():
            return self.installment_item.start_date

        installment = previous_installments.latest('installment_date')
        previous_installment_date = installment.installment_date

        return previous_installment_date

    @property
    def next_installment_amount(self):
        """Calculate the next installment amount."""
        return self.installment_item.amount_due - self.amount

    @property
    def previous_installment_amount(self):
        """Get the previous installment amount."""
        previous_installments = self.__class__.objects.filter(
            installment_item=self.installment_item, installment_date__lt=self.installment_date)
        if not previous_installments.exists():
            return self.installment_item.deposit_amount

        installment = previous_installments.latest('installment_date')
        previous_installment_amount = installment.amount
        return previous_installment_amount

    @property
    def summary(self):
        """Get the installment summary."""
        # TODO Create a summary of the installment (customer, item, price, paid amount, when, remaining)    # noqa
        return {}

    def calculate_next_installment_date(self):
        """Calculate the next installment date."""
        if not self.installment_item.is_cleared:
            self.next_installment_date = self.installment_date + timedelta(30)

    def update_installment_order_item(self):
        """Update installment item of the installment made."""
        if self.installment_item:
            self.installment_item.amount_paid += self.amount

            if self.installment_item.amount_paid >= self.installment_item.total_amount:
                self.installment_item.is_cleared = True
                self.installment_item.payment_status = "FULLY PAID"

            self.installment_item.save()

    def validate_direct_installment_has_installment_item(self):
        """Validate direct installment has an installment item."""
        if self.is_direct_installment and not self.installment_item:
            msg = 'A direct installment requires an installment item to be specified'
            raise ValidationError({'direct_installment': msg})

    def validate_installment_item_is_not_cleared(self):
        """Validate that the installment item is not cleared before processing an installment."""
        if self.installment_item:
            self.installment_item.refresh_from_db()
            if self.installment_item.is_cleared or not self.installment_item.quantity_awaiting_clearance:   # noqa
                customer_name = self.installment_item.order.customer.full_name
                customer_gender = self.installment_item.order.customer.gender
                item_name = self.installment_item.cart_item.catalog_item.inventory_item.item.item_name   # noqa
                customer_pronoun = 'His' if customer_gender == 'MALE' else 'Her'
                raise ValidationError(
                    {'installment item':
                        "Please select a different item to process installments for {}. "
                        "{} {} is already cleared".format(
                            customer_name, customer_pronoun, item_name)})

    def process_installment(self, new_installment=True, previous_amount=None):
        """Process installement."""
        if self.installment_item:
            self.installment_item.refresh_from_db()
            quantity_on_partial_deposit = 0
            self.installment_item.end_date = None
            self.installment_item.is_cleared = False
            if new_installment:
                self.installment_item.amount_paid += self.amount
                self.installment_item.total_installments += self.amount
            else:
                amount_diff = self.amount - previous_amount
                self.installment_item.amount_paid += amount_diff
                self.installment_item.total_installments += amount_diff

            no_of_clearable_items = float(
                self.installment_item.amount_paid) / float(
                    self.installment_item.unit_price) if self.installment_item.unit_price else 0    # noqa

            if no_of_clearable_items:
                quantity_on_partial_deposit = 1

            self.installment_item.quantity_cleared = int(no_of_clearable_items)
            self.installment_item.quantity_on_partial_deposit = quantity_on_partial_deposit

            if self.installment_item.amount_paid >= self.installment_item.total_amount:
                self.installment_item.end_date = timezone.now()
                self.installment_item.is_cleared = True
                self.installment_item.payment_status = "FULLY PAID"

            self.installment_item.save()

            order = self.installment_item.order
            instant_order_items = InstantOrderItem.objects.filter(
                order=order, is_canceled=False)
            installment_order_items = InstallmentsOrderItem.objects.filter(
                order=order, is_canceled=False)

            if instant_order_items.exists() and instant_order_items.filter(
                    is_cleared=False).exists():
                # We cannot clear the order since some valid instant order items
                # are not cleared
                return

            if installment_order_items.exists() and installment_order_items.filter(
                    is_cleared=False).exists():
                # We cannot clear the order since some valid installments order items
                # are not cleared
                return

            order.is_cleared = True
            order.save()
            return

    def clean(self) -> None:
        """Clean the installment model."""
        self.validate_direct_installment_has_installment_item()
        self.validate_installment_item_is_not_cleared()
        super().clean()

    def save(self, *args, **kwargs):
        """Perform pre save and post save actions."""
        self.calculate_next_installment_date()
        super().save(*args, **kwargs)

        self.order_transaction.order.is_cleared = True
        installment_order_items = InstallmentsOrderItem.objects.filter(
            order=self.order_transaction.order)
        if installment_order_items.exists():
            for installment_order_item in installment_order_items:
                if not installment_order_item.is_cleared:
                    self.order_transaction.order.is_cleared = False
                    break

        self.order_transaction.order.save()
        self.refresh_from_db()
        order_transaction = self.order_transaction
        transaction = order_transaction.transaction
        payment = Payment.objects.filter(transaction_guid=transaction.id).first()
        if self.balance:
            if payment:
                payment.balance_amount = self.balance
                payment.save()
            transaction.balance = self.balance
            order_transaction.balance = self.balance
            transaction.save()
            order_transaction.save()

    class Meta:
        """Meta class for installment model."""

        ordering = ['-installment_date']
