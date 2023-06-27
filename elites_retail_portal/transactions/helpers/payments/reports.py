"""Payments reports file."""

import pytz
import datetime

from elites_retail_portal.transactions.models import Payment


def create_report_data(payments):
    """Create reports data."""
    payments_data = []
    totals_data = {}
    total_paid_amount = 0
    for payment in payments:
        data = {
            'account_number': payment.account_number,
            'balance_amount': payment.balance_amount,
            'customer': payment.customer.full_name if payment.customer else '',
            'encounter': payment.encounter.receipt_number if payment.encounter else "",
            'final_amount': payment.final_amount,
            'is_confirmed': 'CONFIRMED' if payment.is_confirmed else "NOT CONFIRMED",
            'is_installment': "INSTALLMENT" if payment.is_processed else "INSANT",
            'is_processed': "PROCESSED" if payment.is_processed else "NOT PROCESSED",
            'paid_amount': payment.paid_amount,
            'payment_code': payment.payment_code,
            'payment_method': payment.payment_method,
            'payment_time': payment.payment_time,
            'required_amount': payment.required_amount,
            'transaction_code': payment.transaction_code,
        }
        payments_data.append(data)
        total_paid_amount += data['paid_amount']

    totals_data['paid_amount'] = total_paid_amount

    return {
        "payments_data": payments_data,
        "totals_data": totals_data,
        }


def generate_payments_report(enterprise_code, start_date=None, end_date=None):
    """Generate sales report."""
    if not start_date and not end_date:
        today = datetime.datetime.now(tz=pytz.timezone('Africa/Nairobi')).date()
        payments = Payment.objects.filter(enterprise=enterprise_code, payment_time__gte=today)
        return create_report_data(payments)

    if start_date and end_date:
        payments = Payment.objects.filter(
            enterprise=enterprise_code, payment_time__gte=start_date,
            payment_time__lte=end_date).order_by('-payment_time')
        return create_report_data(payments)

    if start_date and not end_date:
        payments = Payment.objects.filter(
            enterprise=enterprise_code, payment_time__gte=start_date).order_by('-payment_time')
        return create_report_data(payments)

    # Has end date and no start date
    payments = Payment.objects.filter(
        enterprise=enterprise_code, payment_time__lte=end_date).order_by('-payment_time')
    return create_report_data(payments)
