"""Orders models file."""
from decimal import Decimal
from datetime import timedelta, date

from django.db import models
from django.db.models import PROTECT, CASCADE
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator

from elites_franchise_portal.common.models import AbstractBase
from elites_franchise_portal.orders.models import CartItem, Cart
from elites_franchise_portal.debit.models import Warehouse, WarehouseItem, WarehouseRecord
from elites_franchise_portal.customers.models import Customer
from elites_franchise_portal.transactions.models import Transaction
from elites_franchise_portal.users.models import retrieve_user_email

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
        Customer, null=False, blank=False, on_delete=models.PROTECT)
    cart_code = models.CharField(null=True, blank=True, max_length=300)
    order_number = models.CharField(null=True, blank=True, max_length=250)
    order_name = models.CharField(null=True, blank=True, max_length=300)
    order_date = models.DateTimeField(
        db_index=True, editable=False, default=timezone.now)
    instant_order_total = models.FloatField(null=True, blank=True)
    installment_order_total = models.FloatField(null=True, blank=True)
    order_total = models.FloatField(null=True, blank=True)
    is_processed = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_cleared = models.BooleanField(default=False)
    is_franchise = models.BooleanField(default=False)

    @property
    def summary(self):
        """Generate Order Summary."""
        instant_order_items = InstantOrderItem.objects.filter(order=self)
        installment_order_items = InstallmentsOrderItem.objects.filter(order=self)
        order_total = 0
        if instant_order_items.exists():
            instant_order_items.values_list('total_amount', flat=True)
            import pdb
            pdb.set_trace()

        if installment_order_items.exists():
            installment_order_items.values_list('total_amount', flat=True)
            import pdb
            pdb.set_trace()

        return {'order_total': order_total}

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

        self.__class__.objects.filter(id=order.id).update(is_processed = True)
        cart = Cart.objects.filter(cart_code=self.cart_code)
        if cart.exists():
            cart.update(is_active = False)

        # send email and sms notification to user

    def compose_order_name(self):
        """Compose a name for the order."""
        order = self.__class__.objects.filter(id=self.id, order_number=self.order_number)
        order_name = ''
        if order.exists():
            instant_order_items = InstantOrderItem.objects.filter(order__in=order)
            installment_order_items = InstallmentsOrderItem.objects.filter(order__in=order)
            names = []
            if instant_order_items:
                for instant_order_item in instant_order_items:
                    names.append(
                        instant_order_item.cart_item.catalog_item.inventory_item.item.item_name)

            if installment_order_items:
                for installment_order_item in installment_order_items:
                    names.append(
                        installment_order_item.cart_item.catalog_item.inventory_item.item.item_name)    # noqa

            order_name = ', '.join(names)

        self.order_name = order_name

    def get_order_total(self):
        """Get order total."""
        instant_order_total = 0
        installment_order_total = 0
        order_total = 0
        instant_items = InstantOrderItem.objects.filter(order=self)
        if instant_items.exists():
            prices = []
            for item in instant_items:
                price = float(item.cart_item.catalog_item.selling_price)
                total_price = price * item.cart_item.closing_quantity
                prices.append(total_price)

            instant_order_total = sum(prices)

        installment_items = InstallmentsOrderItem.objects.filter(
            order=self)
        if installment_items.exists():
            prices = []
            for item in installment_items:
                price = float(item.cart_item.catalog_item.selling_price)
                total_price = price * item.cart_item.closing_quantity
                prices.append(total_price)

            installment_order_total = sum(prices)

        order_total = instant_order_total + installment_order_total
        self.instant_order_total = instant_order_total
        self.installment_order_total = installment_order_total
        self.order_total = order_total

    def clean(self) -> None:
        """Clean order."""
        self.compose_order_name()
        self.get_order_total()
        return super().clean()

    def __str__(self) -> str:
        """Represent an order in string format."""
        order_representation = f'{self.customer.full_name} {self.order_name} {self.order_number}'
        return order_representation

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
    confirmation_status = models.CharField(
        null=False, blank=False, max_length=250,
        choices=ORDER_CONFIRMATION_STATUS_CHOICES, default=PENDING)
    total_amount = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=True, blank=True, default=0)
    amount_paid = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=True, blank=True, default=0)
    payment_is_processed = models.BooleanField(default=False)
    payment_status = models.CharField(
        max_length=250, choices=PAYMENT_STATUS_CHOICES, default=NOT_PAID)
    no_of_items_cleared = models.IntegerField(default=0)
    no_of_items_awaiting_clearance = models.IntegerField(default=0)
    no_of_items_returned = models.IntegerField(default=0)
    is_cleared = models.BooleanField(default=False)

    @property
    def unit_price(self):
        """Get the price per item."""
        quantity = self.quantity if self.quantity else 1
        unit_price = float(self.total_amount) / quantity

        return unit_price

    def validate_item_exists_in_inventory_or_cleared_from_store(self):
        """Validate that item exists in catalog, inventory and store."""
        inventory_item = self.cart_item.catalog_item.inventory_item
        inventory_summary = inventory_item.summary
        quantity_in_inventory = inventory_summary['available_quantity']
        if self.quantity > quantity_in_inventory:
            # Check quantity in store.
            order_item = self.cart_item.catalog_item.inventory_item.item
            warehouse_item = WarehouseItem.objects.get(item=order_item, franchise=self.franchise)
            warehouse_item_summary = warehouse_item.summary
            quantity_in_warehouse = warehouse_item_summary['total_quantity']
            if self.quantity > quantity_in_warehouse:
                raise ValidationError(
                    {'quantity': 'There are not enough items in warehouse to fulfil this order'})

    def get_total_amount(self):
        """Get total for the order item."""
        self.total_amount = Decimal(float(self.cart_item.selling_price) * self.quantity)   # noqa

    def get_quantity(self):
        """Get the quantity being ordered."""
        if self.quantity == 0:
            self.quantity = self.cart_item.closing_quantity

    def get_no_of_items_awaiting_clearance(self):
        """Get the number of items awaiing clearance."""
        self.no_of_items_awaiting_clearance = self.quantity - self.no_of_items_cleared

    def clean(self) -> None:
        """Clean Order Item."""
        self.validate_item_exists_in_inventory_or_cleared_from_store()
        return super().clean()

    def save(self, *args, **kwargs):
        """Perform pre save and post save actions."""
        self.get_quantity()
        self.get_total_amount()
        self.get_no_of_items_awaiting_clearance()
        super().save(*args, **kwargs)

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

    deposit_amount = models.FloatField(null=True, blank=True, default=0)
    amount_due = models.DecimalField(
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
    no_of_items_with_full_deposit = models.IntegerField(default=0)
    no_of_items_with_partial_deposit = models.IntegerField(default=0)
    no_of_items_without_deposit = models.IntegerField(null=True, blank=True)

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

    def initialize_no_of_items_without_deposit(self):
        """Initialize the number of items that do not have a deposit."""
        if not self.no_of_items_without_deposit:
            self.no_of_items_without_deposit = self.quantity

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

    def get_amount_due(self):
        """Calculate amount due."""
        amount_due = 0
        if self.amount_paid < self.total_amount:
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
        self.initialize_no_of_items_without_deposit()
        self.get_total_amount()
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

    def initialize_balance(self):
        """Initialize Balance."""
        if not self.balance:
            self.balance = self.amount

    def clean(self) -> None:
        """Clean Order Transaction model."""
        self.initialize_balance()
        return super().clean()

    def process_order_transaction(self):
        """Process a transaction for an order."""
        instant_order_items = InstantOrderItem.objects.filter(
            order=self.order, is_cleared=False)
        installment_order_items = InstallmentsOrderItem.objects.filter(
            order=self.order, is_cleared=False)

        if instant_order_items.exists():
            instant_order_items_totals = instant_order_items.values_list(
                'total_amount', flat=True)
            instant_order_items_total_amount = sum(instant_order_items_totals)
            if self.balance >= instant_order_items_total_amount:
                for instant_order_item in instant_order_items:
                    updates = {
                        'no_of_items_awaiting_clearance': 0,
                        'no_of_items_cleared': instant_order_item.no_of_items_awaiting_clearance,
                        'is_cleared': True,
                        'payment_status': 'PAID',
                        'amount_paid': instant_order_item.total_amount,
                    }
                    instant_order_items.filter(id=instant_order_item.id).update(**updates)

                new_balance = Decimal(self.balance) - Decimal(instant_order_items_total_amount)
                self.balance = new_balance
                self.__class__.objects.filter(id=self.id).update(balance=new_balance)

            else:
                for instant_order_item in instant_order_items:
                    no_of_clearable_items = int(
                        float(self.balance) / instant_order_item.unit_price)
                    deficit = Decimal(instant_order_item.total_amount) - Decimal(self.balance)  # noqa
                    new_balance = float(self.balance) % instant_order_item.unit_price
                    instant_order_item.no_of_items_cleared = no_of_clearable_items
                    instant_order_item.save()
                    self.balance = new_balance
                    self.__class__.objects.filter(id=self.id).update(balance=new_balance)

        if installment_order_items.exists():
            installment_order_items_totals = installment_order_items.values_list(
                'total_amount', flat=True)
            installment_order_items_total_amount = sum(installment_order_items_totals)
            if self.balance >= installment_order_items_total_amount:
                for installment_order_item in installment_order_items:
                    if not installment_order_item.deposit_amount:
                        installment_order_item.amount_paid = installment_order_item.total_amount    # noqa
                        installment_order_item.save()
                        new_balance = Decimal(self.balance) - Decimal(
                            installment_order_items_total_amount)
                        self.balance = new_balance
                        self.__class__.objects.filter(id=self.id).update(balance=new_balance)
                        # TODO check any other fields that require processing

                    else:
                        # TODO clear item and transfer balance to wallet
                        pass
            else:
                installment_order_items = installment_order_items.order_by('-order__order_date')    # noqa
                for installment_order_item in installment_order_items:
                    if not installment_order_item.deposit_amount:
                        installment_order_item.deposit_amount = self.balance if self.balance <= installment_order_item.total_amount else installment_order_item.total_amount    # noqa
                        installment_order_item.amount_paid = installment_order_item.deposit_amount
                        installment_order_item.save()
                        self.balance = Decimal(self.balance) - installment_order_item.amount_paid
                    else:
                        if self.balance <= Decimal(installment_order_item.amount_due):
                            installment_amount = self.balance
                            installment_data = {
                                'created_by': installment_order_item.created_by,
                                'updated_by': installment_order_item.updated_by,
                                'franchise': installment_order_item.franchise,
                                'installment_item': installment_order_item,
                                'amount': installment_amount,
                            }
                            Installment.objects.create(**installment_data)
                        else:
                            # TODO clear an item using an installment
                            installment_amount = installment_order_item.amount_due
                            order_transaction = self.__class__.objects.filter(id=self.id).first()
                            order_transaction.balance -= installment_amount
                            new_balance = order_transaction.balance
                            self.__class__.objects.filter(id=self.id).update(balance=new_balance)
                            installment_data = {
                                'created_by': installment_order_item.created_by,
                                'updated_by': installment_order_item.updated_by,
                                'franchise': installment_order_item.franchise,
                                'installment_item': installment_order_item,
                                'amount': installment_amount,
                            }
                            Installment.objects.create(**installment_data)

        else:
            # Order is present but there are no order items
            # TODO Push the balance to Customer's wallet.

            pass

        order_transaction = self.__class__.objects.filter(id=self.id).first()
        self.transaction._meta.model.objects.filter(
            id=self.transaction.id).update(balance=order_transaction.balance)

        # TODO Assert that the order processing updates the transaction itself too

    def save(self, *args, **kwargs):
        """Perform pre save and post save actions."""
        super().save(*args, **kwargs)
        self.process_order_transaction()

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
    """Installement model."""

    installment_code = models.CharField(null=True, blank=True, max_length=300)
    installment_item = models.ForeignKey(
        InstallmentsOrderItem, null=False, blank=False, on_delete=CASCADE)
    amount = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=False, blank=False)
    installment_date = models.DateTimeField(db_index=True, default=timezone.now)
    next_installment_date = models.DateField(null=True, blank=True)

    @property
    def previous_installment_date(self):
        """Calculate the next installment date."""
        previous_installment_date = None
        previous_installments = self.__class__.objects.filter(
            installment_item=self.installment_item, installment_date__lt=self.installment_date)
        if previous_installments.exists():
            installment = previous_installments.latest('installment_date')
            previous_installment_date = installment.installment_date
            return previous_installment_date

        return previous_installment_date

    @property
    def next_installment_amount(self):
        """Calculate the next installment amount."""
        return self.installment_item.amount_due - self.amount

    @property
    def previous_installment_amount(self):
        """Get the previous installment amount."""
        previous_installment_amount = None
        previous_installments = self.__class__.objects.filter(
            installment_item=self.installment_item, installment_date__lt=self.installment_date)
        if previous_installments.exists():
            installment = previous_installments.latest('installment_date')
            previous_installment_amount = installment.amount
            return previous_installment_amount
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
        installment_order_items = self.installment_item._meta.model.objects.filter(
            id=self.installment_item.id)
        installment_order_item = installment_order_items.first()
        installment_order_item.amount_paid += self.amount
        installment_order_item_updates = {
            'amount_paid': installment_order_item.amount_paid,
        }
        if self.installment_item.amount_paid >= self.installment_item.total_amount:
            self.installment_item.is_cleared = True
            installment_order_item_updates['is_cleared'] = True

        installment_order_items.update(**installment_order_item_updates)
        return

    def validate_installment_item_is_not_cleared(self):
        """Validate that the installment item is not cleared before processing an installment."""
        self.installment_item.refresh_from_db()
        if self.installment_item.is_cleared:
            customer_name = self.installment_item.order.customer.full_name
            customer_gender = self.installment_item.order.customer.gender
            item_name = self.installment_item.cart_item.catalog_item.inventory_item.item.item_name
            customer_pronoun = 'His' if customer_gender == 'MALE' else 'Her'
            raise ValidationError(
                {'installment item':
                    f"Please select a different item to process installments for {customer_name}. { customer_pronoun} {item_name} is already cleared"}) # noqa

    def clean(self) -> None:
        """Clean the installment model."""
        self.validate_installment_item_is_not_cleared()
        return super().clean()

    def save(self, *args, **kwargs):
        """Perform pre save and post save actions."""
        from elites_franchise_portal.orders.helpers.orders import (
            process_installment,)
        self.calculate_next_installment_date()
        super().save(*args, **kwargs)
        self.update_installment_order_item()
        process_installment(self)

    class Meta:
        """Meta class for installment model."""

        ordering = ['-installment_date']
