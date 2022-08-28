"""Order views file."""

from elites_franchise_portal.debit.models.sales import PENDING
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from elites_franchise_portal.catalog.models import CatalogItem
from elites_franchise_portal.common.views import BaseViewMixin
from elites_franchise_portal.orders.models import (
    Order, InstallmentsOrderItem, Installment,
    InstantOrderItem, OrderTransaction)
from elites_franchise_portal.orders.models import Cart
from elites_franchise_portal.debit.models import Sale, SaleRecord
from elites_franchise_portal.orders import serializers
from elites_franchise_portal.debit.tasks import process_sale
from elites_franchise_portal.orders.helpers.orders import refresh_order
from elites_franchise_portal.transactions.models import Payment

class OrderViewSet(BaseViewMixin):
    """Order viewset class."""

    queryset = Order.objects.all()
    serializer_class = serializers.OrderSerializer

    @action(detail=True, methods=['post'])
    def update_order_items(self, request, *args, **kwargs):
        order = self.get_object()
        updated_order_items_data = request.data['updated_order_items_data']
        new_catalog_items_data = request.data['new_catalog_items_data']
        additional_payments = request.data['additional_payments']
        audit_fields = {
            "created_by": self.request.user.id,
            "updated_by": self.request.user.id,
            "franchise": self.request.user.franchise,
            }
        if updated_order_items_data:
            for order_item_data in updated_order_items_data:
                quantity = order_item_data['quantity']
                order_type = order_item_data['order_type']
                order_item_id = order_item_data['order_item']
                confirmation_status = order_item_data['status'] if order_item_data['status'] else 'PENDING'
                if order_type == 'INSTANT':
                    instant_item = InstantOrderItem.objects.filter(id=order_item_id)
                    instant_item.update(quantity=quantity, confirmation_status=confirmation_status)

                if order_type == 'INSTALLMENT':
                    installment_item = InstallmentsOrderItem.objects.filter(id=order_item_id)
                    installment_item.update(quantity=quantity, confirmation_status=confirmation_status)

        if new_catalog_items_data:
            cart = Cart.objects.get(cart_code = order.cart_code)
            Cart.objects.filter(
                id=cart.id).update(customer=order.customer, is_active=True, is_checked_out=False)
            sale = cart.sale
            if not sale:
                sale = Sale.objects.create(customer=order.customer, **audit_fields)
            for catalog_item_data in new_catalog_items_data:
                catalog_item = CatalogItem.objects.get(
                    id=catalog_item_data['catalog_item'])
                quantity = catalog_item_data['quantity']
                sale_type = catalog_item_data['sale_type']
                selling_price = catalog_item_data['unit_price']
                sale_record_payload = {
                    'catalog_item': catalog_item,
                    'sale': sale,
                    'quantity_sold': quantity,
                    'selling_price': selling_price,
                    'sale_type': sale_type,
                }
                SaleRecord.objects.create(**sale_record_payload, **audit_fields)
            process_sale(sale, order)

        if additional_payments:
            for payment in additional_payments:
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

        refresh_order(order)

        serializer = serializers.OrderSerializer(order, many=False)

        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

class InstantOrderItemViewSet(BaseViewMixin):
    """Instant Order Item Viewset class."""

    queryset = InstantOrderItem.objects.all()
    serializer_class = serializers.InstantOrderItemSerializer


class InstallmentsOrderItemViewSet(BaseViewMixin):
    """Installment order item Viewset class."""

    queryset = InstallmentsOrderItem.objects.all()
    serializer_class = serializers.InstallmentsOrderItemSerializer


class InstallmentViewSet(BaseViewMixin):
    """Installment Viewset class."""

    queryset = Installment.objects.all().order_by('-installment_date')
    serializer_class = serializers.InstallmentSerializer


class OrderTransactionViewSet(BaseViewMixin):
    """Order Transactions Viewset class."""

    queryset = OrderTransaction.objects.all()
    serializer_class = serializers.OrderTransactionSerializer
