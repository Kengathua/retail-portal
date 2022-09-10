"""Customer Encounters models file."""

from django.db import models
from django.db.models import Q
from django.contrib.auth import get_user_model
from elites_franchise_portal.common.models import AbstractBase
from elites_franchise_portal.customers.models import Customer
from elites_franchise_portal.catalog.models import (
    CatalogItem, ReferenceCatalog)

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator

ENCOUNTER_PROCESSING_STATUS_CHOICES = (
    ('FAILED', 'FAILED'),
    ('PENDING', 'PENDING'),
    ('ONGOING', 'ONGOING'),
    ('SUCCESS', 'SUCCESS'),
    ('STALLED', 'STALLED'),
    ('CANCELED', 'CANCELED'),
)

PENDING = 'PENDING'


class Encounter(AbstractBase):
    """Customer encounter model."""

    customer = models.ForeignKey(
        Customer, null=True, blank=True, on_delete=models.PROTECT)
    billing = models.JSONField(null=False, blank=False)
    payments = models.JSONField(null=True, blank=True)
    served_by = models.JSONField(null=True, blank=True)
    submitted_amount = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=True, blank=True)
    payable_amount = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=True, blank=True)
    balance_amount = models.DecimalField(
        max_digits=30, decimal_places=2, validators=[MinValueValidator(0.00)],
        null=True, blank=True)
    processing_status = models.CharField(
        max_length=300, choices=ENCOUNTER_PROCESSING_STATUS_CHOICES,
        default=PENDING)
    stalling_reason = models.TextField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)

    def check_customer(self):
        if not self.customer:
            user = get_user_model().objects.filter(
                Q(id=self.created_by)| Q(id=self.updated_by) | Q(
                    guid=self.created_by)| Q(guid=self.updated_by))
            if user.exists():
                user = user.first()
                customer = Customer.objects.filter(
                    enterprise_user=user, enterprise=self.enterprise)
                if customer.exists():
                    customer = customer.first()
                    self.customer = customer

    def validate_billing(self):
        """Valdiate new sale encounter data."""
        for bill in self.billing:
            catalog_item = CatalogItem.objects.filter(id=bill['catalog_item'])
            if not catalog_item.exists():
                raise ValidationError(
                    {'catalog_item': f"This item {bill['item_name']} does not exist"})

            catalog_item = catalog_item.first()
            reference_catalog = ReferenceCatalog.objects.get(catalog_item=catalog_item)
            if bill['sale_type'] == 'INSTANT':
                if bill['quantity'] > catalog_item.quantity \
                        or bill['quantity'] > reference_catalog.quantity:
                    quantity = bill['quantity']
                    item_name = catalog_item.inventory_item.item.item_name
                    raise ValidationError(
                        {'quantity': '{} - Billed quantity {} is more '
                         'than the available quantity of {}'.format(
                            item_name, quantity, catalog_item.quantity)})

            if bill['sale_type'] == 'INSTALLMENT':
                pass

            if float(bill['unit_price']) < float(catalog_item.threshold_price):
                item_name = catalog_item.inventory_item.item.item_name
                raise ValidationError(
                    {'price': 'The threshold price for {} is {}'.format(
                        item_name, catalog_item.threshold_price)})

    def clean(self) -> None:
        """Clean the encounter model."""
        if not self.processing_status == 'STALLED':
            self.validate_billing()
        super().clean()

    def save(self, *args, **kwargs):
        """Perform pre save and post save actins."""
        self.check_customer()
        super().save(*args, **kwargs)
        from elites_franchise_portal.encounters.tasks import (
            process_customer_encounter)
        encounter = self.__class__.objects.filter(id=self.id).first()
        if encounter and not self.processing_status == 'STALLED':
            process_customer_encounter.delay(encounter.id)
            # process_customer_encounter(encounter.id)
            for bill in encounter.billing:
                if bill['sale_type'] == 'INSTANT':
                    catalog_item = CatalogItem.objects.get(id=bill['catalog_item'])
                    reference_catalogs = ReferenceCatalog.objects.filter(catalog_item=catalog_item)
                    reference_catalog = reference_catalogs.first()
                    available_quantity = reference_catalog.available_quantity
                    staged_quantity = reference_catalog.quantity - bill['quantity']
                    quantity = staged_quantity \
                        if staged_quantity <= available_quantity else available_quantity
                    reference_catalogs.update(quantity=quantity)

    # TODO Create a stall button to stall an encounter.
    # NOTE Add a fuctionality to send feedback to the customer advising them
    # on optimal quantities they can purchase
