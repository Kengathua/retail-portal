"""Transactions serializers file."""

from rest_framework.fields import CharField

from elites_retail_portal.transactions import models
from elites_retail_portal.common.serializers import BaseSerializerMixin


class TransactionSerializer(BaseSerializerMixin):
    """Transaction Serializer class."""

    customer_name = CharField(source="customer.full_name", read_only=True)

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
