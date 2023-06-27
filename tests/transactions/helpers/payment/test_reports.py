"""."""

import pytest

from elites_retail_portal.enterprises.models import Enterprise
from elites_retail_portal.transactions.models import Payment
from elites_retail_portal.transactions.helpers.payments.reports import generate_payments_report

from model_bakery import baker
pytestmark = pytest.mark.django_db


def test_generate_payments_report():
    """."""
    franchise = baker.make(Enterprise, name='Elites Age Supermarket')
    enterprise_code = franchise.enterprise_code
    payment = baker.make(
        Payment, account_number='+254712345678', required_amount='1', enterprise=enterprise_code)

    assert payment
    assert Payment.objects.count() == 1
    
    generate_payments_report(enterprise_code)