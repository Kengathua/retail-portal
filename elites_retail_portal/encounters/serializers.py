"""Encounter models serializers file."""

from rest_framework.fields import SerializerMethodField, ReadOnlyField

from elites_retail_portal.common.serializers import BaseSerializerMixin
from elites_retail_portal.encounters import models


class EncounterSerializer(BaseSerializerMixin):
    """Encounter serializer class."""
    customer_name = ReadOnlyField(source='customer.full_name')
    cart = ReadOnlyField(source='cart.heading')
    order = ReadOnlyField(source='order.heading')
    sales_person_name = ReadOnlyField(source='sales_person.full_name')

    class Meta:
        """Encounter Meta class."""

        model = models.Encounter
        fields = '__all__'
