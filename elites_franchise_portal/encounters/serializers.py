"""Encounter models serializers file."""

from rest_framework.fields import SerializerMethodField, ReadOnlyField

from elites_franchise_portal.common.serializers import BaseSerializerMixin
from elites_franchise_portal.encounters import models


class EncounterSerializer(BaseSerializerMixin):
    """Encounter serializer class."""
    customer_name = SerializerMethodField()
    cart = SerializerMethodField()
    order = SerializerMethodField()
    sales_person_name = ReadOnlyField(source='sales_person.full_name')

    def get_customer_name(self, encounter):
        customer_name = None
        if encounter.customer:
            customer_name = encounter.customer.full_name
        return customer_name

    def get_cart(self, encounter):
        cart_code = None
        if encounter.cart:
            cart_code = encounter.cart.cart_code
        return cart_code

    def get_order(self, encounter):
        order_name = None
        if encounter.order:
            order_name = encounter.order.order_name

        return order_name

    class Meta:
        """Encounter Meta class."""

        model = models.Encounter
        fields = '__all__'
