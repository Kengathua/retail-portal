"""Common models for Elites Age franchise portal."""

import uuid
from django.db import models
from django.utils import timezone

from elites_franchise_portal.users.models import retrieve_user_email

GENDER_CHOICES = (
    ('MALE', 'MALE'),
    ('FEMALE', 'FEMALE'),
    ('OTHER', 'OTHER')
)

ID_TYPE_CHOICES = (
    ('NATIONAL ID', 'NATIONAL ID')
    ('MILITARY ID', 'MILITARY ID')
    ('PASSPORT', 'PASSPORT')
)


class BaseModel(models.Model):
    """Base for all models."""

    id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, primary_key=True, auto_created=True)
    created_on = models.DateTimeField(
        db_index=True, editable=False, default=timezone.now)
    created_by = models.UUIDField(editable=False)
    updated_on = models.DateTimeField(db_index=True, default=timezone.now)
    updated_by = models.UUIDField()
    creator = retrieve_user_email('created_by')
    updater = retrieve_user_email('updated_by')

    def retain_created_on_and_created_by(self):
        """Retain values for created_on and created_by fields on update."""
        try:
            initial = self.__class__.objects.get(pk=self.pk)
            self.created_on = initial.created_on
            self.created_by = initial.created_by
        except self.__class__.DoesNotExist:
            pass

    def save(self, *args, **kwargs):
        """Record today as the update date."""
        self.updated_on = timezone.now()
        self.full_clean(exclude=None)
        self.retain_created_on_and_created_by()
        super(BaseModel, self).save(*args, **kwargs)

    class Meta:
        """Initialize as meta class.

        order by descending dates starting with updated by.
        """

        abstract = True
        ordering = ('-updated_on', '-created_on')


class AbstractBase(BaseModel):
    """Base Class for all models that are applicable to enterprises."""

    enterprise = models.CharField(null=False, blank=False, max_length=250,)

    def save(self, *args, **kwargs):
        """Override save."""
        super(AbstractBase, self).save(*args, **kwargs)

    class Meta:
        """Initialize it as an abstract class."""

        abstract = True


class BioData(AbstractBase):
    """A person's bio data  abstract model"""

    title = models.CharField(max_length=256, null=True, blank=True)
    first_name = models.CharField(max_length=256)
    other_names = models.CharField(max_length=256, null=True, blank=True)
    last_name = models.CharField(max_length=256)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=24, choices=GENDER_CHOICES, null=True, blank=True)
    join_date = models.DateTimeField(default=timezone.now)
    id_no = models.CharField(max_length=256, null=True, blank=True)
    id_type = models.CharField(max_length=300, choices=ID_TYPE_CHOICES)
    phone_no = models.CharField(max_length=256, null=True, blank=True)
    email = models.EmailField(blank=True, null=True)

    class Meta:
        """Initialize it as an abstract class."""

        abstract = True
