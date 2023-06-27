"""Order views file."""

from django.db import transaction

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from elites_retail_portal.catalog.models import CatalogItem
from elites_retail_portal.common.views import BaseViewMixin
from elites_retail_portal.orders.models import (
    Order, InstallmentsOrderItem, Installment,
    InstantOrderItem, OrderTransaction)
from elites_retail_portal.orders.models import Cart, CartItem
from elites_retail_portal.orders import serializers, filters
from elites_retail_portal.orders.helpers.orders import refresh_order
from elites_retail_portal.transactions.models import Payment, Transaction
from elites_retail_portal.encounters.models import Encounter


class OrderViewSet(BaseViewMixin):
    """Order viewset class."""

    queryset = Order.objects.all()
    serializer_class = serializers.OrderSerializer
    filterset_class = filters.OrderFilter
    search_fields = (
        'order_name', 'order_number',
        'customer__first_name', 'customer__customer_number', 'customer__last_name',
        'customer__other_names',)

    @action(detail=True, methods=['post'])
    def update_order_items(self, request, *args, **kwargs):
        """Update order items."""
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
                confirmation_status = order_item_data['status'] if order_item_data['status'] else 'PENDING' # noqa
                if order_type == 'INSTANT':
                    instant_item = InstantOrderItem.objects.filter(id=order_item_id)
                    instant_item.update(quantity=quantity, confirmation_status=confirmation_status)

                if order_type == 'INSTALLMENT':
                    installment_item = InstallmentsOrderItem.objects.filter(id=order_item_id)
                    installment_item.update(
                        quantity=quantity, confirmation_status=confirmation_status)

        if new_catalog_items_data:
            cart = Cart.objects.get(cart_code=order.cart_code)
            Cart.objects.filter(
                id=cart.id).update(customer=order.customer, is_active=True, is_checked_out=False)
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
    search_fields = (
        'cart_item__catalog_item__inventory_item__item__item_name',
        'cart_item__catalog_item__inventory_item__item__barcode',
        'cart_item__catalog_item__inventory_item__item__item_code',
    )


class InstallmentViewSet(BaseViewMixin):
    """Installment Viewset class."""

    queryset = Installment.objects.all().order_by('-installment_date')
    serializer_class = serializers.InstallmentSerializer
    filterset_class = filters.InstallmentFilter
    search_fields = (
        'installment_code', 'amount', 'balance', 'note',
        'installment_item__cart_item__catalog_item__inventory_item__item__item_name',
        'installment_item__cart_item__catalog_item__inventory_item__item__barcode',
        'order_transaction__order__customer__first_name',
        'order_transaction__order__customer__last_name',
        'order_transaction__order__customer__other_names',
        'order_transaction__order__customer__customer_number',
        'order_transaction__order__order_name', 'order_transaction__order__order_number')

    @transaction.atomic()
    def create(self, request, *args, **kwargs):
        """Installment post."""
        audit_fields = {
            "created_by": self.request.user.id,
            "updated_by": self.request.user.id,
            "enterprise": self.request.user.enterprise,
            }

        installment_item = InstallmentsOrderItem.objects.get(id=request.data['installment_item'])

        if installment_item.is_cleared and installment_item.total_amount <= installment_item.amount_paid:   # noqa
            error = {'item': 'The order item {} if already cleared'.format(
                installment_item.cart_item.catalog_item.inventory_item.item.item_name)}
            return Response(data=error, status=status.HTTP_400_BAD_REQUEST)

        customer = installment_item.order.customer

        encounter = Encounter.objects.filter(order_guid=installment_item.order.id).first()
        payment_payload = {
            'payment_code': request.data.get('payment_code', None),
            'account_number': customer.account_number or customer.phone_no or customer.customer_number, # noqa
            'customer': customer,
            'paid_amount': request.data['amount'],
            'payment_method': request.data.get('payment_method', 'CASH'),
            'encounter': encounter,
            'is_installment': True,
        }
        payment = Payment.objects.create(**payment_payload, **audit_fields)
        payment.refresh_from_db()

        transaction_payload = {
            'account_number': customer.account_number or customer.phone_no or customer.customer_number, # noqa
            'amount': request.data['amount'],
            'transaction_means': request.data.get('payment_method', 'CASH'),
            'customer': customer,
        }

        transaction = Transaction.objects.create(**transaction_payload, **audit_fields)
        transaction.refresh_from_db()
        payment.transaction_guid = transaction.id
        payment.is_confirmed = True
        payment.is_processed = True
        payment.save()

        order_transaction_payload = {
            'amount': transaction.balance,
            'order': installment_item.order,
            'transaction': transaction,
            'is_installment': True,
        }
        order_transaction = OrderTransaction.objects.create(
            **order_transaction_payload, **audit_fields)
        transaction.is_processed = True
        transaction.balance = 0
        transaction.save()

        installment_payload = {
            'order_transaction': order_transaction,
            'installment_item': installment_item,
            'amount': request.data['amount'],
            'balance': 0,
            'note': request.data.get('note', None),
            'is_direct_installment': True
        }

        order_transaction.balance = 0
        if float(installment_item.amount_due) < float(request.data['amount']):
            balance = float(request.data['amount']) - float(installment_item.amount_due)
            installment_payload['amount'] = installment_item.amount_due
            installment_payload['balance'] = balance
            transaction.balance = balance
            order_transaction.balance = balance
            transaction.save()

        installment = Installment.objects.create(**installment_payload, **audit_fields)
        installment.process_installment()
        installment.refresh_from_db()

        order_transaction.is_processed = True
        order_transaction.save()

        serializer = serializers.InstallmentSerializer(installment, many=False)

        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    @transaction.atomic()
    def update(self, request, *args, **kwargs):
        """Installments update."""
        installment = self.get_object()
        previous_amount = installment.amount
        order_transaction = installment.order_transaction
        transaction = order_transaction.transaction
        payment = Payment.objects.get(transaction_guid=transaction.id)

        payment.paid_amount = request.data['amount']
        payment.final_amount = request.data['amount']
        payment.updated_by = self.request.user.id
        payment.save()

        transaction.amount = request.data['amount']
        transaction.updated_by = self.request.user.id
        transaction.save()

        order_transaction.amount = request.data['amount']
        order_transaction.updated_by = self.request.user.id
        order_transaction.save()

        installment.amount = request.data['amount']
        installment.updated_by = self.request.user.id
        installment.save()
        installment.process_installment(new_installment=False, previous_amount=previous_amount)
        installment.refresh_from_db()

        serializer = serializers.InstallmentSerializer(installment, many=False)

        return Response(data=serializer.data, status=status.HTTP_200_OK)


class OrderTransactionViewSet(BaseViewMixin):
    """Order Transactions Viewset class."""

    queryset = OrderTransaction.objects.all()
    serializer_class = serializers.OrderTransactionSerializer
    filterset_class = filters.OrderTransactionFilter
