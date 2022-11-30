"""Mpesa models file."""

from django.db import models
from elites_retail_portal.common.models import AbstractBase
from django_cryptography.fields import encrypt


class MpesaAuthorization(AbstractBase):
    """Mpesa Authorization model."""

    consumer_key = encrypt(models.CharField(max_length=300))
    consumer_secret = encrypt(models.CharField(max_length=300))
    pass_key = encrypt(models.CharField(max_length=300))
    till_number = models.CharField(max_length=300, null=True, blank=True)
    paybill_number = models.CharField(max_length=300, null=True, blank=True)
    business_short_code = models.CharField(max_length=300, null=True, blank=True)
