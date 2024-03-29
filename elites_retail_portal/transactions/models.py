"""Transactions file model."""

from decimal import Decimal

from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

from elites_retail_portal.customers.models import Customer
from elites_retail_portal.common.models import AbstractBase
from elites_retail_portal.encounters.models import Encounter

TRANSACTION_TYPES = (
    ('DEPOSIT', 'DEPOSIT'),
    ('WITHDRAW', 'WITHDRAW'),
    ('TRANSFER', 'TRANSFER'),
)

TRANSACTION_MEANS = (
    ('PDQ', 'PDQ'),
    ('CASH', 'CASH'),
    ('CARD', 'CARD'),
    ('WALLET', 'WALLET'),
    ('MPESA TILL', 'MPESA TILL'),
    ('MPESA PAYBILL', 'MPESA PAYBILL'),
    ('BANK WIRE TRANSFER', 'BANK WIRE TRANSFER'),
)

RESERVATION_TYPES = (
    ('FLAT', 'FLAT'),
    ('PERCENTAGE', 'PERCENTAGE'),
    ('NO RESERVATION', 'NO RESERVATION'),
)

RESERVE_AT_CHOICES = (
    ('WALLET', 'WALLET'),
    ('OTHER', 'OTHER'),
)

PAYMENT_REQUEST_STATUS_CHOICES = (
    ('PENDING', 'PENDING'),
    ('SUCCESS', 'SUCCESS'),
    ('FAILED', 'FAILED'),
)

PAYMENT_STATUS_CHOICES = (
    ('FAILED', 'FAILED'),
    ('PENDING', 'PENDING'),
    ('ONGOING', 'ONGOING'),
    ('SUCCESS', 'SUCCESS'),
    ('STALLED', 'STALLED'),
    ('CANCELED', 'CANCELED'),
    ('RECEIVED', 'RECEIVED'),
)

NO_RESERVATION = 'NO RESERVATION'
WALLET = 'WALLET'
CASH = 'CASH'
DEPOSIT = 'DEPOSIT'
PENDING = 'PENDING'
PAYBILL = 'PAYBILL'
RECEIVED = 'RECEIVED'


class Transaction(AbstractBase):
    """Transactions model."""

    transaction_code = models.CharField(max_length=250, null=True, blank=True)
    payment_code = models.CharField(max_length=300, null=True, blank=True)
    customer = models.ForeignKey(
        Customer, null=True, blank=True, on_delete=models.PROTECT)
    wallet_code = models.CharField(max_length=250, null=True, blank=True)
    account_number = models.CharField(max_length=250, null=True, blank=True)
    amount = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=False, blank=False)
    balance = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=True, blank=True)
    reservation_amount = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=True, blank=True)
    reservation_type = models.CharField(
        max_length=300, null=True, blank=True, choices=RESERVATION_TYPES,
        default=NO_RESERVATION)
    reserve_at = models.CharField(
        max_length=300, null=True, blank=True, choices=RESERVE_AT_CHOICES, default=WALLET)
    transaction_time = models.DateTimeField(
        db_index=True, default=timezone.now)
    transaction_type = models.CharField(
        max_length=250, choices=TRANSACTION_TYPES, default=DEPOSIT)
    transaction_means = models.CharField(
        max_length=250, choices=TRANSACTION_MEANS, default=CASH)
    is_processed = models.BooleanField(default=False)
    status = models.CharField(
        max_length=300, choices=PAYMENT_STATUS_CHOICES, default=RECEIVED)

    def initialize_balance(self):
        """Initialize transaction balance."""
        if not self.balance and not self.is_processed:
            self.balance = self.amount

    def get_customer(self):
        """Get customer."""
        if self.account_number and not self.customer:
            customers = Customer.objects.filter(
                account_number=self.account_number, enterprise=self.enterprise)
            self.customer = customers.first()

    def validate_non_cash_transactions_have_account_number(self):
        """Validate non cash transactions have an account number.

        Restore this functionality once the golang module for handling
        integrated payments is built
        """
        if self.transaction_means != CASH:
            if not self.account_number:
                pass
                # raise ValidationError(
                #     {'account_number': 'Please add the account number to the transaction'})

    def clean(self) -> None:
        """Clean transactions model."""
        self.validate_non_cash_transactions_have_account_number()
        return super().clean()

    def save(self, *args, **kwargs):
        """Perform pre save and post save actions."""
        self.initialize_balance()
        self.get_customer()
        super().save(*args, **kwargs)


class Payment(AbstractBase):
    """Payment Requests model."""

    payment_time = models.DateTimeField(db_index=True, default=timezone.now)
    payment_code = models.CharField(max_length=300, null=True, blank=True)
    transaction_code = models.CharField(max_length=300, null=True, blank=True)
    account_number = models.CharField(max_length=300, null=True, blank=True)
    customer = models.ForeignKey(
        Customer, null=True, blank=True, on_delete=models.PROTECT)
    encounter = models.ForeignKey(
        Encounter, null=True, blank=True, on_delete=models.PROTECT)
    required_amount = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=True, blank=True)
    paid_amount = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=False, blank=False)
    balance_amount = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=True, blank=True, default=0)
    final_amount = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=True, blank=True)
    payment_method = models.CharField(max_length=300, null=True, blank=True, default=CASH)
    status = models.CharField(max_length=300, choices=PAYMENT_STATUS_CHOICES, default=RECEIVED)
    is_confirmed = models.BooleanField(default=False)
    is_processed = models.BooleanField(default=False)
    is_installment = models.BooleanField(default=False)
    transaction_guid = models.UUIDField(null=True, blank=True)

    def make_payment_request(
        self, service, amount=None, request_from_number=None, client_account_number=None, service_type=None):   # noqa
        """Make a payment request."""
        if service == 'M-PESA':
            if self.account_number and not request_from_number:
                customers = Customer.objects.filter(
                    Q(account_number=self.account_number) | Q(
                        phone_no=self.account_number) | Q(
                            customer_number=self.account_number), enterprise=self.enterprise)
                if len(customers) == 1:
                    customer = customers.first()
                    phone_number = customer.phone_number
                else:
                    raise ValidationError(
                        {'customers': f'Found {len(customers)} customers attached to this account number'}) # noqa

            elif self.account_number and request_from_number:
                # TODO Validate the phone number is a valid phone number
                # TODO check if account number is a customer number
                phone_number = request_from_number

            else:
                phone_number = request_from_number

            payment_request_data = {
                'created_by': self.created_by,
                'updated_by': self.updated_by,
                'enterprise': self.enterprise,
                'payment_id': self.id,
                'client_account_number': client_account_number,
                'request_from_account_number': phone_number,
                'requested_amount': amount if amount else self.required_amount,
                'service': service,
                'service_type': PAYBILL if not service_type else service_type
            }
            PaymentRequest.objects.create(**payment_request_data)

    def save(self, *args, **kwargs):
        """Perform pre save and post save actions."""
        self.final_amount = Decimal(float(self.paid_amount) - float(self.balance_amount))
        super().save(*args, **kwargs)


class PaymentRequest(AbstractBase):
    """Payment Requests model."""

    payment_id = models.UUIDField(null=True, blank=True)
    business_account_number = models.CharField(
        max_length=300, null=True, blank=True)  # ie paybill
    client_account_number = models.CharField(
        max_length=300, null=True, blank=True)  # ie account_no
    request_from_account_number = models.CharField(
        max_length=300, null=True, blank=True)    # customer phone_no
    phone_number = models.CharField(
        max_length=300, null=True, blank=True)    # (M-PESA) - customer phone_no
    business_short_code = models.CharField(
        max_length=200, null=True, blank=True)
    business_passkey = models.CharField(
        max_length=200, null=True, blank=True)
    requested_amount = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=False, blank=False)
    paid_amount = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=True, blank=True)
    service = models.CharField(max_length=300)
    service_type = models.CharField(max_length=300)
    status = models.CharField(
        max_length=300, choices=PAYMENT_REQUEST_STATUS_CHOICES, default=PENDING)
    message = models.CharField(max_length=300, null=True, blank=True)
    receipt_no = models.CharField(max_length=300, null=True, blank=True)    # customer phone_no
    is_confirmed = models.BooleanField(default=False)
    auto_process_payment = models.BooleanField(default=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    checkout_request_id = models.CharField(max_length=300, null=True, blank=True)

    def process_payment_request(self, business_passkey=None):
        """Process payment request."""
        if self.service == 'M-PESA':
            from elites_retail_portal.transactions.helpers.payments.gateways import MpesaGateWay
            mpesa_gateway = MpesaGateWay()
            mpesa_request_payload = {
                'PartyA': self.business_account_number,
                'PartyB': self.client_account_number,
                'PhoneNumber': self.request_from_account_number,
                'BusinessShortCode': self.business_short_code,
                'Amount': self.requested_amount,
                'PassKey': business_passkey if business_passkey else self.business_passkey
                }

            mpesa_request_payload['PartyA'] = 600989
            mpesa_request_payload['BusinessShortCode'] = '174379'
            mpesa_request_payload['PassKey'] = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'   # noqa
            response_status_code, response_data = mpesa_gateway.stk_push_request(mpesa_request_payload) # noqa
            if response_status_code == 200:
                updates = {
                    'status': 'SUCCESS',
                    'checkout_request_id': response_data['CheckoutRequestID'],
                    'message': response_data['CustomerMessage']
                }
                self.__class__.objects.filter(id=self.id).update(**updates)
            else:
                self.__class__.objects.filter(id=self.id).update(status='FAILED')

            if self.payment_id:
                payment_request = self.__class__.objects.get(id=self.id)
                if payment_request.is_confirmed:
                    amount = payment_request.paid_amount
                    payment = Payment.objects.get(id=self.payment_id)
                    payment.paid_amount = amount
                    payment.is_confirmed = True
                    payment.save()

                # Payment.objects.filter(
                    # id=payment.id).update(paid_amount=amount, is_confirmed=True)

    def save(self, *args, **kwargs):
        """Perform pre save and post save actions."""
        super().save(*args, **kwargs)
        if self.auto_process_payment:
            self.process_payment_request()
