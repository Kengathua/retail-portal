"""Customer models file."""

from django.db import models
from django.utils import timezone
from elites_retail_portal.common.models import BioData
from elites_retail_portal.users.models import retrieve_user_email
from django.core.exceptions import ValidationError
from elites_retail_portal.users.models import User

GENDER_CHOICES = (
    ('MALE', 'MALE'),
    ('FEMALE', 'FEMALE'),
    ('OTHER', 'OTHER')
)


class Customer(BioData):
    """Customer model."""

    customer_number = models.CharField(max_length=256, db_index=True)
    account_number = models.CharField(max_length=300, null=True, blank=True)
    join_date = models.DateTimeField(default=timezone.now)
    is_vip = models.BooleanField(default=False)
    is_enterprise = models.BooleanField(default=False)
    enterprise_user = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.PROTECT)
    pushed_to_edi = models.BooleanField(default=False)
    creator = retrieve_user_email('created_by')
    updater = retrieve_user_email('updated_by')

    def assign_customer_number(self):
        """Assign a customer a unique number."""
        pass

    def assign_account_number(self):
        """Assign a cutomer a unique account number."""
        pass

    def validate_unique_customer_number(self):
        """Validate a customer's customer number."""
        if self.customer_number:
            customer = self.__class__.objects.filter(
                customer_number=self.customer_number, enterprise=self.enterprise)
            if customer.exists():
                raise ValidationError(
                    {'customer_number': 'A customer with this customer number already exists.'})

    def validate_unique_account_number(self):
        """Validate a customer's account number."""
        if self.account_number:
            customer = self.__class__.objects.filter(
                account_number=self.account_number, enterprise=self.enterprise)
            if customer.exists():
                raise ValidationError(
                    {'account_number': 'A customer with this account number already exists.'})

    def validate_unique_phone_no(self):
        """Validate the phone number used is unique."""
        if self.phone_no:
            customer = self.__class__.objects.filter(
                phone_no=self.phone_no, enterprise=self.enterprise)
            if customer.exists():
                raise ValidationError(
                    {'phone_number': 'A customer with this phone number already exists.'})

    def validate_on_site_customer_has_user(self):
        """Validate on site customer has a user assigned to them."""
        if self.is_enterprise:
            if not self.enterprise_user:
                raise ValidationError(
                    {'user': 'Please assign a user to the customer'})

    def process_site_customer(self):
        """Process site customer."""
        if self.enterprise_user:
            self.is_enterprise = True

    def clean(self) -> None:
        """Clean the customer model."""
        is_new = False if self.__class__.objects.filter(
            id=self.id).exists() else True
        if is_new:
            self.validate_unique_customer_number()
            self.validate_unique_account_number()
            self.validate_unique_phone_no()
            self.validate_on_site_customer_has_user()
        return super().clean()

    def __str__(self) -> str:
        """Str representation for customer instance."""
        customer_representation = f'{self.first_name} {self.other_names} {self.last_name} -> {self.phone_no}'   # noqa
        return customer_representation

    def save(self, *args, **kwargs):
        """Perform pre save and post save actions."""
        self.assign_customer_number()
        self.assign_account_number()
        self.process_site_customer()
        super().save(*args, **kwargs)
