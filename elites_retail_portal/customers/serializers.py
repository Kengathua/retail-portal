"""Wallet serializers file."""

from rest_framework.fields import ReadOnlyField, CharField
from rest_framework import serializers
from elites_retail_portal.customers import models
from elites_retail_portal.common.serializers import BaseSerializerMixin


class CustomerSerializer(BaseSerializerMixin):
    """Customer serializer class."""

    full_name = ReadOnlyField()

    class Meta:
        """Serializer Meta class."""

        model = models.Customer
        fields = '__all__'
