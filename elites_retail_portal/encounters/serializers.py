"""Encounter models serializers file."""

from django.db.models import Q
from django.contrib.auth import get_user_model

from rest_framework.fields import ReadOnlyField, SerializerMethodField

from elites_retail_portal.common.serializers import BaseSerializerMixin
from elites_retail_portal.encounters import models
from elites_retail_portal.enterprises.models import Enterprise
from elites_retail_portal.enterprises.serializers import EnterpriseSerializer


class EncounterSerializer(BaseSerializerMixin):
    """Encounter serializer class."""

    customer_name = ReadOnlyField(source='customer.full_name')
    cart = ReadOnlyField(source='cart.heading')
    order = ReadOnlyField(source='order.heading')
    sales_person_name = ReadOnlyField(source='sales_person.full_name')
    served_by_name = SerializerMethodField(source='served_by.full_name')
    enterpise_details = SerializerMethodField()

    def get_served_by_name(self, instance):
        """Get served by name."""
        if instance.served_by:
            return instance.served_by.full_name

        user = get_user_model().objects.filter(
            Q(id=instance.created_by) | Q(id=instance.updated_by) | Q(
                guid=instance.created_by) | Q(guid=instance.updated_by),
            is_active=True).first()
        if user:
            return user.get_full_name()

    def get_enterpise_details(self, instance):
        """Get enterprise details."""
        enterprise = Enterprise.objects.get(enterprise_code=instance.enterprise)
        return EnterpriseSerializer(enterprise).data

    class Meta:
        """Encounter Meta class."""

        model = models.Encounter
        fields = '__all__'
