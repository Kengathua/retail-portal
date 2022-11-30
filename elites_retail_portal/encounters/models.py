"""Customer Encounters models file."""

from decimal import Decimal

from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth import get_user_model
from elites_retail_portal.common.models import AbstractBase
from elites_retail_portal.customers.models import Customer
from elites_retail_portal.encounters.helpers.validators import validate_billing
from elites_retail_portal.enterprises.models import Staff

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator

ENCOUNTER_PROCESSING_STATUS_CHOICES = (
    ('FAILED', 'FAILED'),
    ('PENDING', 'PENDING'),
    ('ONGOING', 'ONGOING'),
    ('BILLING DONE', 'BILLING DONE'),
    ('SUCCESS', 'SUCCESS'),
    ('STALLED', 'STALLED'),
    ('CANCELED', 'CANCELED'),
)

PENDING = 'PENDING'


class Encounter(AbstractBase):
    """Customer encounter model."""

    billing = models.JSONField(null=False, blank=False)
    payments = models.JSONField(null=True, blank=True)
    customer = models.ForeignKey(
        Customer, null=True, blank=True, on_delete=models.PROTECT)
    served_by = models.ForeignKey(
        Staff, null=True, blank=True, on_delete=models.PROTECT, related_name='served_by_staff')
    sales_person = models.ForeignKey(
        Staff, null=True, blank=True, on_delete=models.PROTECT,  related_name='sales_person_staff')
    submitted_amount = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=True, blank=True)
    payable_amount = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=True, blank=True)
    balance_amount = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=True, blank=True)
    total_deposit = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=True, blank=True, default=0)
    processing_status = models.CharField(
        max_length=300, choices=ENCOUNTER_PROCESSING_STATUS_CHOICES,
        default=PENDING)
    stalling_reason = models.TextField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    cart_guid = models.UUIDField(null=True, blank=True)
    order_guid = models.UUIDField(null=True, blank=True)
    receipt_number = models.CharField(max_length=300, null=True, blank=True)
    encounter_number = models.CharField(max_length=300, null=True, blank=True)
    encounter_date = models.DateTimeField(db_index=True, default=timezone.now)

    @property
    def cart(self):
        """Cart used to process the encounter."""
        from elites_retail_portal.orders.models import Cart
        cart = None
        if self.cart_guid:
            cart = Cart.objects.get(id=self.cart_guid)

        return cart

    @property
    def order(self):
        """Order used to process the encounter."""
        from elites_retail_portal.orders.models import Order
        order = None
        if self.order_guid:
            order = Order.objects.get(id=self.order_guid)

        return order

    @property
    def cashier(self):
        """Cashier who served the customer at the counter."""
        return None

    def get_submitted_amount(self):
        """Get the total amount submitted by the customer."""
        if self.payments and not self.submitted_amount:
            payments_made = []
            for payment in self.payments:
                amount = payment['amount']
                payments_made.append(float(amount))

            self.submitted_amount = sum(payments_made)

    def get_payable_amount(self):
        """Get payable amount."""
        instant_sale_amounts = []
        payable_deposits = []
        if self.billing:
            for bill in self.billing:
                if bill['sale_type'] == 'INSTANT':
                    total = float(bill['quantity']) * float(bill['unit_price'])
                    instant_sale_amounts.append(total)

                if bill['sale_type'] == 'INSTALLMENT':
                    deposit = bill.get('deposit', 0) or 0
                    payable_deposits.append(float(deposit))

        self.total_deposit = sum(payable_deposits)
        self.payable_amount = sum(instant_sale_amounts) + self.total_deposit

    def get_balance_amount(self):
        self.balance_amount = Decimal(float(self.submitted_amount) - float(self.payable_amount))

        if self.submitted_amount < self.payable_amount:
            msg = "The submitted amount KSh. {:,.2f} is less to the total payable amount KSh. {:,.2f} by KSh. {:,.2f}".format(
                self.submitted_amount, self.payable_amount, self.balance_amount)
            raise ValidationError({'submitted_amount': msg})

    def check_customer(self):
        if not self.customer:
            user = get_user_model().objects.filter(
                Q(id=self.created_by)| Q(id=self.updated_by) | Q(
                    guid=self.created_by)| Q(guid=self.updated_by), is_active=True)
            if user.exists():
                user = user.first()
                customer = Customer.objects.filter(
                    enterprise_user=user, enterprise=self.enterprise)
                if customer.exists():
                    customer = customer.first()
                    self.customer = customer

    def create_receipt_number(self):
        if not self.receipt_number:
            import random
            receipt_number = random.randint(1000, 100000)
            self.receipt_number = f'EAS/{receipt_number}'

        # TODO Create a function to generate receipts taking into account creating the receipt number.
        # Consider using the encounter number in the receipt number too
        # Abbreviate the Retailer in the receipt number

    def create_encounter_number(self):
        if not self.encounter_number:
            import random
            encounter_number = random.randint(1000, 100000)
            self.encounter_number = f'EAS/{encounter_number}'

    def clean(self) -> None:
        """Clean the encounter model."""
        if not self.processing_status == 'STALLED':
            validate_billing(self)
        # TODO Check for this error (SAMSUNG S-001 TV is not hooked up to an active Allocated Inventory. Please set that up first)
        super().clean()

    def save(self, *args, **kwargs):
        """Perform pre save and post save actins."""
        from elites_retail_portal.encounters.tasks import (
            process_customer_encounter)
        self.get_submitted_amount()
        self.get_payable_amount()
        self.get_balance_amount()
        self.check_customer()
        self.create_receipt_number()
        self.create_encounter_number()
        super().save(*args, **kwargs)
        encounter = self.__class__.objects.filter(id=self.id).first()
        if encounter and self.processing_status == 'PENDING':
            # process_customer_encounter.delay(encounter.id)
            process_customer_encounter(encounter.id)

    # TODO Create a stall button to stall an encounter.
    # NOTE Add a fuctionality to send feedback to the customer advising them
    # on optimal quantities they can purchase

    class Meta:
        """Meta class for encounter model."""
        ordering = ['-encounter_date']
