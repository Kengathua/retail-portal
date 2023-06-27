"""Inventory views file."""

import pytz
import datetime
from xhtml2pdf import pisa

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from django.conf import settings
from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import get_template

from elites_retail_portal.common.views import BaseViewMixin
from elites_retail_portal.debit.models import (
    Inventory, InventoryItem, InventoryRecord)
from elites_retail_portal.debit import serializers
from elites_retail_portal.debit import filters
from elites_retail_portal.debit.models.inventory import InventoryInventoryItem
from elites_retail_portal.items.models import Item
from elites_retail_portal.debit.stock.reports import (
    generate_stock_report, generate_items_history)
from elites_retail_portal.enterprises.models import Enterprise
from elites_retail_portal.common.utils import _write_excel_file


class InventoryViewSet(BaseViewMixin):
    """Inventory Viewset class."""

    queryset = Inventory.objects.all().order_by('inventory_name')
    serializer_class = serializers.InventorySerializer
    filterset_class = filters.InventoryFilter
    search_fields = (
        'inventory_name', 'inventory_code', 'inventory_type')


class InventoryItemViewSet(BaseViewMixin):
    """Inventory Item Viewset class."""

    queryset = InventoryItem.objects.all().order_by('item__item_name')
    serializer_class = serializers.InventoryItemSerializer
    filterset_class = filters.InventoryItemFilter
    search_fields = (
        'item__item_name', 'item__item_model__model_name',
        'item__item_model__model_code', 'item__barcode',
        'item__item_code', 'item__make_year',
    )

    @action(detail=False, methods=['post'])
    def generate_stock_report(self, request, *args, **kwargs):
        """Generate members upload template."""
        enterprise_code = self.request.user.enterprise
        data = generate_stock_report(enterprise_code)

        return Response(data=data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def generate_items_history(self, request, *args, **kwargs):
        """Generate members upload template."""
        enterprise_code = self.request.user.enterprise
        item_id = self.request.data.get('item', None)
        item = Item.objects.filter(id=item_id).first() if item_id else None  # noqa
        data = generate_items_history(enterprise_code, item)

        return Response(data=data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def export_stock_report(self, request, *args, **kwargs):
        """Download members upload template."""
        headers = (
            'item', 'quantity_in_catalog', 'quantity_in_warehouse', 'quantity_in_inventory',
            'order_number', 'status', 'marked_price', 'selling_price', 'threshold_price')

        labels = {
            'item': 'Item',
            'quantity_in_catalog': 'Quantity in Catalog',
            'quantity_in_warehouse': 'Quantity in Warehouse',
            'quantity_in_inventory': 'Quantity in Inventory',
            'status': 'Status',
            'marked_price': 'Marked Price',
            'selling_price': 'Selling Price',
            'threshold_price': 'Threshold Price'
        }

        now = timezone.now()
        enterprise_code = self.request.user.enterprise
        SITE_NAME = Enterprise.objects.get(enterprise_code=enterprise_code).name
        file_name = '{}-stock-report-as-at-{}'.format(SITE_NAME, now.date())

        item_id = self.request.data.get('item', None)
        item = Item.objects.filter(id=item_id).first() if item_id else None  # noqa

        file_type = self.request.data.get('file_type', None)
        data = generate_stock_report(enterprise_code)

        if file_type == "PDF":
            template = get_template("stock_report.html")
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

        excel_file = _write_excel_file(headers, labels, {}, data['stock_data'])
        content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response = HttpResponse(content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename={file_name}.xlsx'
        response.content = excel_file

        return response

    def export_item_history_report(self, request, *args, **kwargs):
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

        # start_date = self.request.data.get('start_date', None)
        # end_date = self.request.data.get('end_date', None)
        item_id = self.request.data.get('item', None)
        item = Item.objects.filter(id=item_id).first() if item_id else None  # noqa

        file_type = self.request.data.get('file_type', None)
        data = generate_stock_report(enterprise_code)

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


class InventoryInventoryItemViewSet(BaseViewMixin):
    """Inventory Inventory Item Viewset class."""

    queryset = InventoryInventoryItem.objects.all().order_by(
        'inventory__inventory_name', 'inventory_item__item__item_name')
    serializer_class = serializers.InventoryInventoryItemSerializer
    filterset_class = filters.InventoryInventoryItemFilter
    search_fields = (
        'inventory__inventory_name', 'inventory__inventory_code',
        'inventory__inventory_type', 'inventory_item__item__item_name',
        'inventory_item__item__item_model__model_name',
        'inventory_item__item__item_model__model_code',
        'inventory_item__item__barcode', 'inventory_item__item__item_code',
        'inventory_item__item__make_year',
        )


class InventoryRecordViewSet(BaseViewMixin):
    """Inventory Record ViewSet class."""

    queryset = InventoryRecord.objects.all().order_by(
        '-updated_on', 'inventory_item__item__item_name')
    serializer_class = serializers.InventoryRecordSerializer
    filterset_class = filters.InventoryRecordFilter
    search_fields = (
        'inventory__inventory_name', 'inventory__inventory_code',
        'inventory__inventory_type', 'inventory_item__item__item_name',
        'inventory_item__item__item_model__model_name',
        'inventory_item__item__item_model__model_code',
        'inventory_item__item__barcode', 'inventory_item__item__item_code',
        'inventory_item__item__make_year', 'record_code', 'record_type', 'removal_type',
        )
