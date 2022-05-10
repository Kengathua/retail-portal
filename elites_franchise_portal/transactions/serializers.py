"""Transactions serializers file."""

from elites_franchise_portal.transactions import models
from elites_franchise_portal.common.serializers import BaseSerializerMixin

class TransactionSerializer(BaseSerializerMixin):
    """Transaction Serializer class."""

    class Meta:
        """Serializer Meta class."""

        model = models.Transaction
        fields = '__all__'

class PaymentSerializer(BaseSerializerMixin):
    """Payment Serializer class."""

    class Meta:
        """Serializer Meta class."""

        model = models.Payment
        fields = '__all__'


class PaymentRequestSerializer(BaseSerializerMixin):
    """Payment Request Serializer class."""

    class Meta:
        """Serializer Meta class."""

        model = models.PaymentRequest
        fields = '__all__'
