"""Sales views  file."""

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from elites_franchise_portal.debit.models import (
    Sale, SaleRecord)
from elites_franchise_portal.debit import serializers
from elites_franchise_portal.common.views import BaseViewMixin
from elites_franchise_portal.catalog.models import CatalogItem
from elites_franchise_portal.customers.models import Customer
from elites_franchise_portal.debit.tasks import process_sale
from elites_franchise_portal.transactions.models import (
    Transaction, Payment)

class SaleViewSet(BaseViewMixin):
    """Sale View class."""

    queryset = Sale.objects.all()
    serializer_class = serializers.SaleSerializer

    @action(detail=True, methods=['post'])
    def new_sale(self, request, *args, **kwargs):
        """Hit custom new sale endpoint."""
        sale = self.get_object()
        customer_id = request.data['customer'] if 'customer' in request.data.keys() else None
        if customer_id:
            customer = Customer.objects.get(id=customer_id)
            if not customer == sale.customer:
                sale.customer = customer
                sale.save()
                sale.refresh_from_db()

        if request.data['billing']:
            sales_records = []
            for bill in request.data['billing']:
                catalog_item = CatalogItem.objects.get(id=bill['catalog_item'])
                quantity = bill['quantity']
                selling_price = bill['unit_price']
                sale_type = bill['sale_type']

                sale_record_payload = {
                    'created_by': sale.created_by,
                    'updated_by': sale.updated_by,
                    'franchise': sale.franchise,
                    'catalog_item': catalog_item,
                    'sale': sale,
                    'quantity_sold': quantity,
                    'selling_price': selling_price,
                    'sale_type': sale_type,
                }

                sale_record = SaleRecord.objects.create(**sale_record_payload)
                sales_records.append(sale_record)

            process_sale(sale)
            if request.data['payments']:
                for payment in request.data['payments']:
                    means = payment['means']
                    amount = payment['amount']
                    if amount:
                        payment_payload = {
                            'created_by': sale.created_by,
                            'updated_by': sale.updated_by,
                            'franchise': sale.franchise,
                            'paid_amount': amount,
                            'customer': sale.customer,
                            'payment_method': means,
                            'is_confirmed': True,
                            'is_processed': True,
                            'required_amount': amount,
                        }
                        Payment.objects.create(**payment_payload)

            serializer = serializers.SaleRecordSerializer(sales_records, many=True)

        return Response(data=serializer.data, status=status.HTTP_201_CREATED)


class SaleRecordViewSet(BaseViewMixin):
    """Sale Record view class."""

    queryset = SaleRecord.objects.all()
    serializer_class = serializers.SaleRecordSerializer
