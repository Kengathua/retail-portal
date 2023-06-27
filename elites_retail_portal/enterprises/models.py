"""Models file for enterprise app."""

from django.db import models
from django.core.exceptions import ValidationError

from elites_retail_portal.common.models import BaseModel, BioData
from elites_retail_portal.common.validators import (
    phoneNumberRegex, enterprise_enterprise_code_validator)
from elites_retail_portal.common.code_generators import generate_enterprise_code

ENTERPRISE_TYPES = (
    ('FRANCHISE', 'FRANCHISE'),
    ('SUPPLIER', 'SUPPLIER'),
    ('INDEPENDENT', 'INDEPENDENT')
)

# TODO Limit the enterprise types to Retailer and Supplier

SOCIAL_PLATFORMS = (
    ('FACEBOOK', 'FACEBOOK'),
    ('TWITTER', 'TWITTER'),
    ('INSTAGRAM', 'INSTAGRAM'),
    ('WHATSAPP', 'WHATSAPP')
)

BUSINESS_TYPE_CHOICES = (
    ('AGENT', 'AGENT'),
    ('SHOP', 'SHOP'),
    ('SUPERMARKET', 'SUPERMARKET'),
    ('WHOLESALE', 'WHOLESALE')
)

SUPPLIER_TYPE_CHOICES = (
    ('IMPORTER', 'IMPORTER'),
    ('SERVICES', 'SERVICES'),
    ('WHOLESALER', 'WHOLESALER'),
    ('DISTRIBUTOR', 'DISTRIBUTOR'),
    ('MANUFACTURER', 'MANUFACTURER'),
    ('DROP SHIPPER', 'DROP SHIPPER'),
    ('SUB CONTRACTOR', 'SUB CONTRACTOR'),
    ('TRADE SHOW REP', 'TRADE SHOW REP'),
    ('INDEPENDENT SUPPLIER', 'INDEPENDENT SUPPLIER'),
)

STAFF_TYPE_CHOICES = (
    ('CASUAL', 'CASUAL'),
    ('CONTRACT', 'CONTRACT'),
    ('EMPLOYEE', 'EMPLOYEE'),
)

EMPLOYEE = 'EMPLOYEE'
FRANCHISE = 'FRANCHISE'
SHOP = 'SHOP'


class Enterprise(BaseModel):
    """Enterprise Model."""

    reg_no = models.CharField(max_length=300, null=True, blank=True)
    name = models.CharField(max_length=300, null=False, blank=False)
    short_name = models.CharField(max_length=300, null=True, blank=True)
    enterprise_code = models.CharField(
        max_length=300, validators=[enterprise_enterprise_code_validator],
        null=True, blank=True, unique=True)
    enterprise_type = models.CharField(
        max_length=300, null=False, blank=False, choices=ENTERPRISE_TYPES, default=FRANCHISE)
    main_branch_code = models.CharField(max_length=300, null=True, blank=True, db_index=True)
    is_main_branch = models.BooleanField(default=True)
    business_type = models.CharField(
        max_length=300, null=True, blank=True, choices=BUSINESS_TYPE_CHOICES, default=SHOP)
    supplier_type = models.CharField(
        max_length=300, null=True, blank=True, choices=SUPPLIER_TYPE_CHOICES)
    dissolution_date = models.DateField(db_index=True, null=True, blank=True)
    dissolution_reason = models.TextField(null=True, blank=True)
    is_cleaned = models.BooleanField(default=False)
    pushed_to_edi = models.BooleanField(default=False)

    # TODO Add elites code to identify enterprise as a whole

    def create_enterprise_code(self):
        """Check and create an enterprise code for new enterprise."""
        if not self.enterprise_code:
            enterprise_code = generate_enterprise_code(self)
            self.enterprise_code = enterprise_code

    def validate_main_branch_exists(self):
        """Validate main branch exists."""
        main_branch_exists = self.__class__.objects.filter(
            enterprise_code=self.main_branch_code).exists()
        if not self.is_main_branch and not self.main_branch_code:
            raise ValidationError({
                'local branch': 'Missing main branch. Please add the code of the main branch'
            })

        elif not self.is_main_branch and not main_branch_exists:
            raise ValidationError(
                {'local branch': 'Mismatching main branch details. Please add a valid main branch code'})   # noqa

        if self.is_main_branch and self.main_branch_code:
            raise ValidationError(
                {'main branch':
                'The enterprise is marked as a main branch. Please remove the main branch code attached to it'}  # noqa
            )

    def clean(self) -> None:
        """Enterprise clean function."""
        self.validate_main_branch_exists()
        return super().clean()

    def save(self, *args, **kwargs):
        """Pre save and post save actions."""
        self.short_name = self.name if not self.short_name else self.short_name
        self.create_enterprise_code()
        return super().save(*args, **kwargs)

    def __str__(self):
        """Enterprise string representation."""
        return self.name

    class Meta:
        """Meta class for Enterprise Model."""

        ordering = ['-name']


class EnterpriseContact(BaseModel):
    """Enterprisees Contacts models."""

    enterprise = models.ForeignKey(
        Enterprise, max_length=250, null=False, blank=False,
        related_name='contact_enterprise', on_delete=models.PROTECT)
    email = models.EmailField(null=True, blank=True)
    phoneNumber = models.CharField(
        validators=[phoneNumberRegex], max_length=16, unique=True,
        null=False, blank=False)
    address = models.TextField(null=True, blank=True)


class Platform(BaseModel):
    """Enterprise social platforms model."""

    enterprise = models.ForeignKey(
        Enterprise, max_length=250, null=False, blank=False,
        related_name='platform_Enterprise', on_delete=models.PROTECT)
    social_platform = models.CharField(
        null=False, blank=False, max_length=250, choices=SOCIAL_PLATFORMS)
    link = models.URLField(null=True, blank=True)
    username = models.CharField(max_length=300, null=True, blank=True)
    account_no = models.CharField(max_length=300, null=True, blank=True)

    def clean(self) -> None:
        """Clean Enterprise online platforms."""
        return super().clean()


class Staff(BioData):
    """Employee model class."""

    staff_number = models.CharField(max_length=300)
    staff_type = models.CharField(
        max_length=300, choices=STAFF_TYPE_CHOICES, default=EMPLOYEE)


class Agent(BioData):
    """Agent model class."""

    agent_number = models.CharField(max_length=300)
