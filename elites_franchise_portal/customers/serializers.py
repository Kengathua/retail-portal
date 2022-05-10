"""Wallet serializers file."""

from elites_franchise_portal.customers import models
from elites_franchise_portal.common.serializers import BaseSerializerMixin


class CustomerSerializer(BaseSerializerMixin):
    """Customer serializer class."""

    class Meta:
        """Serializer Meta class."""

        model = models.Customer
        fields = '__all__'
