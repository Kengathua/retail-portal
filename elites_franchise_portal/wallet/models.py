"""Wallet models file."""

from django.db import models

from djmoney.models.fields import MoneyField
from elites_franchise_portal.common.models import AbstractBase
from elites_franchise_portal.customers.models import Customer

CURRENCY_CHOICES = (
    ('KSH', 'KSH'),
    ('USD', 'USD'),
    ('EUR', 'EUR'),
)

WALLET_RECORD_TYPE_CHOICES = (
    ('DEPOSIT', 'DEPOSIT'),
    ('WITHDRAWAL', 'WITHDRAWAL'),
)


class AbstractWallet(AbstractBase):
    """Abstract wallet model."""

    wallet_code = models.CharField(max_length=150, unique=True)
    balance = MoneyField(
        max_digits=19, decimal_places=2, default_currency='KES')

    class Meta:
        """Wallet abstract class."""

        abstract = True


class Wallet(AbstractWallet):
    """Wallet model."""

    owner = models.OneToOneField(
        Customer, null=False, blank=False, editable=False, on_delete=models.PROTECT)


class AnonymousWallet(AbstractWallet):
    """Anonymous wallet model."""

    pass


class WalletRecord(AbstractBase):
    """Wallet Record model."""

    wallet_code = models.CharField(max_length=50)
    record_type = models.CharField(
        choices=WALLET_RECORD_TYPE_CHOICES, max_length=300)
    amount_recorded = MoneyField(
        max_digits=19, decimal_places=2, default_currency='KES')
