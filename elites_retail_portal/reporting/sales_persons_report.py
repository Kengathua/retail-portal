"""Sales persons reports file."""

import pytz
import datetime

from elites_retail_portal.enterprises.models import Staff
from elites_retail_portal.enterprises.serializers import StaffSerializer
from elites_retail_portal.debit.models import Sale, SaleItem
from elites_retail_portal.debit.helpers.sales import create_report_data
from elites_retail_portal.encounters.models import Encounter


def get_sales_person_sales_data(
        enterprise_code, staff_members=[], start_date=None, end_date=None):
    """Get sales person sales data."""
    sales_data = []

    if not staff_members:
        staff_members = Staff.objects.filter(enterprise=enterprise_code)
        if staff_members.exists():
            encounters = Encounter.objects.filter(
                enterprise=enterprise_code, sales_person__in=staff_members)
    else:
        encounters = Encounter.objects.filter(
            enterprise=enterprise_code, sales_person__in=staff_members)

    for staff_member in staff_members:
        encounters = Encounter.objects.filter(sales_person=staff_member, order_guid__isnull=False)
        order_ids = list(map(str, encounters.values_list('order_guid', flat=True)))

        if not start_date and not end_date:
            today = datetime.datetime.now(tz=pytz.timezone('Africa/Nairobi')).date()
            sales = Sale.objects.filter(
                enterprise=enterprise_code, order_id__in=order_ids, sale_date__gte=today)
            sales = Sale.objects.filter(enterprise=enterprise_code, order__id__in=order_ids)
            sale_items = SaleItem.objects.filter(sale__in=sales).order_by('-sale__sale_date')
            sales_person_data = StaffSerializer(staff_member).data
            report_data = create_report_data(sale_items)

            sales_data.append({
                "sales_person": sales_person_data,
                "report_data": report_data,
            })
            continue

        if start_date and end_date:
            sales = Sale.objects.filter(
                enterprise=enterprise_code, order__id__in=order_ids, sale_date__gte=start_date,
                sale_date__lte=end_date).order_by('-sale_date')
            sale_items = SaleItem.objects.filter(sale__in=sales).order_by('-sale__sale_date')
            sales_person_data = StaffSerializer(staff_member).data
            report_data = create_report_data(sale_items)
            sales_data.append({
                "sales_person": sales_person_data,
                "report_data": report_data,
            })
            continue

        if start_date and not end_date:
            sales = Sale.objects.filter(
                enterprise=enterprise_code, order__id__in=order_ids,
                sale_date__gte=start_date).order_by('-sale_date')
            sale_items = SaleItem.objects.filter(sale__in=sales).order_by('-sale__sale_date')
            sales_person_data = StaffSerializer(staff_member).data
            report_data = create_report_data(sale_items)
            sales_data.append({
                "sales_person": sales_person_data,
                "report_data": report_data,
            })
            continue

        sales = Sale.objects.filter(
            enterprise=enterprise_code, order__id__in=order_ids,
            sale_date__lte=end_date).order_by('-sale_date')
        sale_items = SaleItem.objects.filter(sale__in=sales).order_by('-sale__sale_date')
        sales_person_data = StaffSerializer(staff_member).data
        report_data = create_report_data(sale_items)
        sales_data.append({
            "sales_person": sales_person_data,
            "report_data": report_data,
        })

    return sales_data
