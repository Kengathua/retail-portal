"""Order Serializers file."""

from rest_framework.fields import CharField, SerializerMethodField
from elites_franchise_portal.common.serializers import BaseSerializerMixin
from elites_franchise_portal.orders import models


class RecordOwnerSerializer(BaseSerializerMixin):
    """
    Attach an owner to a record.

    Rethink through this.
    """

    def create(self, cleaned_data):
        """Use contextlib here."""
        try:
            if cleaned_data['owner']:
                pass

        except KeyError:
            cleaned_data['owner'] = self.request.user

        return super().create(cleaned_data)


class CartSerializer(BaseSerializerMixin):
    """Cart Serializer class."""

    order_number = SerializerMethodField()
    order_name = SerializerMethodField()
    customer_name = CharField(source='customer.full_name', read_only=True)
    encounter_number = CharField(source='encounter.encounter_number', read_only=True)

    def get_order_number(self, cart):
        order_number = ''
        if cart.order:
            order_number = cart.order.order_number

        return order_number

    def get_order_name(self, cart):
        order_name = ''
        if cart.order:
            order_name = cart.order.order_name

        return order_name

    # owner_details = SerializerMethodField()

    # def get_owner_details(self, record):
    #     """Serialize details of the business partner that a user is linked to."""
    #     user = User.objects.get(id=record.owner.id)
    #     return {
    #         'first_name': user.first_name,
    #         'last_name': user.last_name,
    #         'email': user.email,
    #     }

    class Meta:
        """Serializer Meta class."""

        model = models.Cart
        fields = '__all__'


class CartItemSerializer(BaseSerializerMixin):
    """Cart Serializer class."""

    item_name = CharField(source='catalog_item.inventory_item.item.item_name', read_only=True)

    class Meta:
        """Serializer Meta class."""

        model = models.CartItem
        fields = '__all__'


class OrderSerializer(BaseSerializerMixin):
    """Order Serializer class."""

    customer_name = CharField(source='customer.full_name', read_only=True)

    class Meta:
        """Serializer Meta class."""

        model = models.Order
        fields = '__all__'


class InstantOrderItemSerializer(BaseSerializerMixin):
    """Instant order item Serializer class."""

    unit_price = CharField(read_only=True)
    item_name = CharField(source='cart_item.catalog_item.inventory_item.item.item_name', read_only=True)
    customer_name = CharField(source='order.customer.full_name', read_only=True)
    order_name = CharField(source='order.order_name', read_only=True)
    order_number = CharField(source='order.order_number', read_only=True)

    class Meta:
        """Serializer Meta class."""

        model = models.InstantOrderItem
        fields = '__all__'


class InstallmentsOrderItemSerializer(BaseSerializerMixin):
    """Installment Order Item Serializer class."""

    unit_price = CharField(read_only=True)
    item_name = CharField(source='cart_item.catalog_item.inventory_item.item.item_name', read_only=True)
    customer_name = CharField(source='order.customer.full_name', read_only=True)
    order_name = CharField(source='order.order_name', read_only=True)
    order_number = CharField(source='order.order_number', read_only=True)

    class Meta:
        """Serializer Meta class."""

        model = models.InstallmentsOrderItem
        fields = '__all__'


class InstallmentSerializer(BaseSerializerMixin):
    """Installment Serializer class."""

    item_name = CharField(source='installment_item.cart_item.catalog_item.inventory_item.item.item_name', read_only=True)
    customer_name = CharField(source='installment_item.order.customer.full_name', read_only=True)
    previous_installment_date = CharField(read_only=True)
    next_installment_amount = CharField(read_only=True)
    previous_installment_amount = CharField(read_only=True)
    class Meta:
        """Serializer Meta class."""

        model = models.Installment
        fields = '__all__'


class OrderTransactionSerializer(BaseSerializerMixin):
    """Order Transaction Serializer class."""

    order_coverage_percentage = SerializerMethodField()
    order_number = CharField(source='order.order_number', read_only=True)
    order_name = CharField(source='order.order_name', read_only=True)
    transaction_time = CharField(source='transaction.transaction_time', read_only=True)

    def get_order_coverage_percentage(self, order_transaction):
        order_total = order_transaction.order.summary['order_total']
        coverage = int((order_transaction.amount / order_total) * 100)

        return coverage

    class Meta:
        """Serializer Meta class."""

        model = models.OrderTransaction
        fields = '__all__'
