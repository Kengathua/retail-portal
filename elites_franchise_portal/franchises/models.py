"""Models file for franchise app."""

from django.db import models
from django.db.models.deletion import PROTECT
from django.core.exceptions import ValidationError

from elites_franchise_portal.common.models import BaseModel
from elites_franchise_portal.common.validators import (
    phoneNumberRegex, franchise_elites_code_validator)
from elites_franchise_portal.common.code_generators import generate_elites_code

FRANCHISE_TYPES = (
    ('AGENT', 'AGENT'),
    ('SHOP', 'SHOP'),
    ('SUPERMARKET', 'SUPERMARKET'),
)

SOCIAL_PLATFORMS = (
    ('FACEBOOK', 'FACEBOOK'),
    ('TWITTER', 'TWITTER'),
    ('INSTAGRAM', 'INSTAGRAM'),
    ('WHATSAPP', 'WHATSAPP')
)

SHOP = 'SHOP'


class Franchise(BaseModel):
    """Franchise Model."""

    reg_no = models.CharField(max_length=300, null=True, blank=True)
    name = models.CharField(max_length=300, null=False, blank=False)
    main_branch_code = models.CharField(max_length=300, null=True, blank=True, db_index=True)
    is_main = models.BooleanField(default=True)
    elites_code = models.CharField(
        max_length=300, validators=[franchise_elites_code_validator],
        null=True, blank=True, unique=True)
    partnership_type = models.CharField(
        max_length=300, null=False, blank=False, choices=FRANCHISE_TYPES, default=SHOP)
    dissolution_date = models.DateField(db_index=True, null=True, blank=True)
    dissolution_reason = models.TextField(null=True, blank=True)

    def validate_main_branch_exists(self):
        """Validate main branch exists."""
        main_branch_exists = self.__class__.objects.filter(
            elites_code=self.main_branch_code).exists()
        if not self.is_main and not self.main_branch_code:
            raise ValidationError({
                'local branch': 'Missing main branch. Please add the code of the main branch'
            })

        elif not self.is_main and not main_branch_exists:
            raise ValidationError(
                {'local branch': 'Mismatching main branch details. Please add a valid main branch code'})   # noqa

        if self.is_main and self.main_branch_code:
            raise ValidationError(
                {'main branch':
                'The franchise is marked as a main branch. Please remove the main branch code attached to it'}  # noqa
            )

    def create_elites_code(self):
        """Check and create a franchise code for new franchise."""
        if not self.elites_code:
            elites_code = generate_elites_code(self)
            self.elites_code = elites_code

    def clean(self) -> None:
        """Franchise clean function."""
        self.validate_main_branch_exists()
        self.create_elites_code()
        return super().clean()

    def __str__(self):
        """Franchisee string representation."""
        return self.name

    class Meta:
        """Meta class for Franchise Model."""

        ordering = ['-name']


class FranchiseContacts(BaseModel):
    """Franchisees Contacts models."""

    franchise = models.ForeignKey(Franchise, max_length=250, null=False,
                                  blank=False, related_name='contact_franchise_name',
                                  on_delete=PROTECT)
    email = models.EmailField(null=True, blank=True)
    phoneNumber = models.CharField(
        validators=[phoneNumberRegex], max_length=16, unique=True,
        null=False, blank=False)
    address = models.TextField(null=True, blank=True)


class Platform(BaseModel):
    """Franchisees social platforms model."""

    franchise = models.ForeignKey(Franchise, max_length=250, null=False,
                                  blank=False, related_name='platform_franchise_name',
                                  on_delete=PROTECT)
    social_platform = models.CharField(
        null=False, blank=False, max_length=250, choices=SOCIAL_PLATFORMS)
    link = models.URLField(null=False, blank=False)

    def clean(self) -> None:
        """Clean Franchise online platforms."""
        return super().clean()
