"""Order views file."""

from django.db import transaction

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from elites_franchise_portal.catalog.models import CatalogItem
from elites_franchise_portal.common.views import BaseViewMixin
from elites_franchise_portal.orders.models import (
    Order, InstallmentsOrderItem, Installment,
    InstantOrderItem, OrderTransaction)
from elites_franchise_portal.orders.models import Cart, CartItem
from elites_franchise_portal.debit.models import Sale
from elites_franchise_portal.orders import serializers, filters
from elites_franchise_portal.debit.tasks import process_sale
from elites_franchise_portal.orders.helpers.orders import refresh_order
from elites_franchise_portal.transactions.models import Payment, Transaction
from elites_franchise_portal.customers.models import Customer

class OrderViewSet(BaseViewMixin):
    """Order viewset class."""

    queryset = Order.objects.all()
    serializer_class = serializers.OrderSerializer
    filterset_class = filters.OrderFilter
    search_fields = (
        'order_name', 'order_number')

    @action(detail=True, methods=['post'])
    def update_order_items(self, request, *args, **kwargs):
        order = self.get_object()
        updated_order_items_data = request.data['updated_order_items_data']
        new_catalog_items_data = request.data['new_catalog_items_data']
        additional_payments = request.data['additional_payments']
        audit_fields = {
            "created_by": self.request.user.id,
            "updated_by": self.request.user.id,
            "enterprise": self.request.user.enterprise,
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
            sale = Sale.objects.get(order=order)
            for catalog_item_data in new_catalog_items_data:
                catalog_item = CatalogItem.objects.get(
                    id=catalog_item_data['catalog_item'])
                quantity = catalog_item_data['quantity']
                order_type = catalog_item_data['sale_type']
                selling_price = catalog_item_data['unit_price']
                payload = {
                    'catalog_item': catalog_item,
                    'cart': cart,
                    'quantity_added': quantity,
                    'selling_price': selling_price,
                    'is_installment': True if order_type == 'INSTALLMENT' else False,
                }
                CartItem.objects.create(**payload, **audit_fields)

            cart.checkout_cart()
            order.process_order()

        if additional_payments:
            for payment in additional_payments:
                means = payment['means']
                amount = payment['amount']
                if amount:
                    payment_payload = {
                        'paid_amount': amount,
                        'customer': order.customer,
                        'payment_method': means,
                        'is_confirmed': True,
                        'is_processed': True,
                        'required_amount': amount,
                    }
                    Payment.objects.create(**payment_payload, **audit_fields)

        refresh_order(order)

        serializer = serializers.OrderSerializer(order, many=False)

        return Response(data=serializer.data, status=status.HTTP_201_CREATED)


class InstantOrderItemViewSet(BaseViewMixin):
    """Instant Order Item Viewset class."""

    queryset = InstantOrderItem.objects.all()
    serializer_class = serializers.InstantOrderItemSerializer
    filterset_class = filters.InstantOrderItemFilter


class InstallmentsOrderItemViewSet(BaseViewMixin):
    """Installment order item Viewset class."""

    queryset = InstallmentsOrderItem.objects.all()
    serializer_class = serializers.InstallmentsOrderItemSerializer
    filterset_class = filters.InstallmentsOrderItemFilter


class InstallmentViewSet(BaseViewMixin):
    """Installment Viewset class."""

    queryset = Installment.objects.all().order_by('-installment_date')
    serializer_class = serializers.InstallmentSerializer

    @transaction.atomic()
    def create(self, request, *args, **kwargs):
        audit_fields = {
            "created_by": self.request.user.id,
            "updated_by": self.request.user.id,
            "enterprise": self.request.user.enterprise,
            }

        installment_item = InstallmentsOrderItem.objects.get(id=request.data['installment_item'])
        customer = Customer.objects.get(id=request.data['customer'])

        payment_payload = {
            'payment_code': request.data['payment_code'],
            'account_number': customer.account_number,
            'customer': customer,
            'paid_amount': request.data['amount'],
            'payment_method': request.data['payment_method'],
        }
        payment = Payment.objects.create(**payment_payload, **audit_fields)
        payment.refresh_from_db()

        transaction_payload = {
            'account_number': customer.account_number,
            'amount': request.data['amount'],
            'transaction_means': request.data['payment_method'],
            'customer': customer,
        }
        transaction = Transaction.objects.create(**transaction_payload, **audit_fields)
        transaction.refresh_from_db()
        payment.transaction_guid = transaction.id
        payment.save()

        order_transaction_payload = {
            'amount': transaction.balance,
            'order': installment_item.order,
            'transaction': transaction,
            'is_installment': True,
        }
        order_transaction = OrderTransaction.objects.create(**order_transaction_payload, **audit_fields)

        installment_payload = {
            'order_transaction': order_transaction,
            'installment_item': installment_item,
            'amount': request.data['amount'],
            'note': request.data['note'],
            'is_direct_installment': True
        }

        installment = Installment.objects.create(**installment_payload, **audit_fields)
        serializer = serializers.InstallmentSerializer(installment, many=False)

        return Response(data=serializer.data, status=status.HTTP_201_CREATED)


class OrderTransactionViewSet(BaseViewMixin):
    """Order Transactions Viewset class."""

    queryset = OrderTransaction.objects.all()
    serializer_class = serializers.OrderTransactionSerializer
    filterset_class = filters.OrderTransactionFilter
