"""Sales views  file."""

import pytz
import datetime
from xhtml2pdf import pisa

from django.conf import settings
from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import get_template

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from elites_retail_portal.debit.models import (
    Sale, SaleItem)
from elites_retail_portal.items.models import Item
from elites_retail_portal.enterprises.models import Enterprise
from elites_retail_portal.debit import serializers, filters
from elites_retail_portal.common.views import BaseViewMixin
from elites_retail_portal.common.utils import _write_excel_file
from elites_retail_portal.debit.helpers.sales import generate_sales_report


class SaleViewSet(BaseViewMixin):
    """Sale View class."""

    queryset = Sale.objects.all().order_by('-sale_date')
    serializer_class = serializers.SaleSerializer
    filterset_class = filters.SaleFilter
    search_fields = (
        'customer__first_name', 'customer__last_name',
        'customer__other_names', 'customer__customer_number',
        'order__order_number', 'sale_code',
    )

    @action(detail=False, methods=['post'])
    def generate_sales_report(self, request, *args, **kwargs):
        """Generate members upload template."""
        enterprise_code = self.request.user.enterprise
        start_date = self.request.data.get('start_date', None)
        end_date = self.request.data.get('end_date', None)
        item_id = self.request.data.get('item', None)
        item = Item.objects.filter(id=item_id).first() if item_id else None  # noqa

        data = generate_sales_report(enterprise_code, item, start_date, end_date)

        return Response(data=data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def export_report(self, request, *args, **kwargs):
        """Download members upload template."""
        headers = (
            'sale_date', 'receipt_number', 'item', 'customer', 'order_number',
            'amount_paid', 'status', 'processing_status', 'quantity_sold',
            'sale_type', 'selling_price', 'total_amount')

        labels = {
            'sale_date': 'Sale Date',
            'receipt_number': 'Receipt Number',
            'item': 'Item',
            'customer': 'Customer',
            'order_number': 'Order Number',
            'amount_paid': 'Amount Paid',
            'status': 'Status',
            'processing_status': 'Processing Status',
            'quantity_sold': 'Quantity Sold',
            'sale_type': 'Sale Type',
            'selling_price': 'Selling Price',
            'total_amount': 'Total Amount',
        }

        now = timezone.now()
        enterprise_code = self.request.user.enterprise
        SITE_NAME = Enterprise.objects.get(enterprise_code=enterprise_code).name
        file_name = '{}-sales-report-as-at-{}'.format(SITE_NAME, now.date())

        start_date = self.request.data.get('start_date', None)
        end_date = self.request.data.get('end_date', None)
        item_id = self.request.data.get('item', None)
        item = Item.objects.filter(id=item_id).first() if item_id else None  # noqa

        file_type = self.request.data.get('file_type', None)
        data = generate_sales_report(enterprise_code, item, start_date, end_date)

        if file_type == "PDF":
            template = get_template("sales_report.html")
            path_to_static = str(settings.STATIC_ROOT).split("/static")[0]
            today = datetime.datetime.now(tz=pytz.timezone('Africa/Nairobi')).date()
            context = {
                'report_preview': {'report_date': today.strftime("%Y%m%d%H%M%S")},
                'data': data,
                'path_to_static': path_to_static
            }
            html = template.render(context)
            response = HttpResponse(content_type='application/pdf')
            pdf_status = pisa.CreatePDF(html, dest=response)

            if pdf_status.err:
                return HttpResponse('Some errors were encountered <pre>' + html + '</pre>')

            return response

        excel_file = _write_excel_file(headers, labels, {}, data['sales_data'])
        content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response = HttpResponse(content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename={file_name}.xlsx'
        response.content = excel_file

        return response


class SaleItemViewSet(BaseViewMixin):
    """Sale Record view class."""

    queryset = SaleItem.objects.all()
    serializer_class = serializers.SaleItemSerializer
    filterset_class = filters.SaleItemFilter
    search_fields = (
        'catalog_item__inventory_item__item__item_name',
        'catalog_item__inventory_item__item__barcode',
        'sale__customer__full_name', 'processing_status',
        'sale_type', 'selling_price', 'total_amount', 'amount_paid'
    )
