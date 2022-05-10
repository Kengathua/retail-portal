"""Order Serializers file."""

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

    class Meta:
        """Serializer Meta class."""

        model = models.CartItem
        fields = '__all__'


class OrderSerializer(BaseSerializerMixin):
    """Order Serializer class."""

    class Meta:
        """Serializer Meta class."""

        model = models.Order
        fields = '__all__'


class InstantOrderItemSerializer(BaseSerializerMixin):
    """Instant order item Serializer class."""

    class Meta:
        """Serializer Meta class."""

        model = models.InstantOrderItem
        fields = '__all__'


class InstallmentsOrderItemSerializer(BaseSerializerMixin):
    """Installment Order Item Serializer class."""

    class Meta:
        """Serializer Meta class."""

        model = models.InstallmentsOrderItem
        fields = '__all__'


class InstallmentSerializer(BaseSerializerMixin):
    """Installment Serializer class."""

    class Meta:
        """Serializer Meta class."""

        model = models.Installment
        fields = '__all__'


class OrderTransactionSerializer(BaseSerializerMixin):
    """Order Transaction Serializer class."""

    class Meta:
        """Serializer Meta class."""

        model = models.OrderTransaction
        fields = '__all__'
