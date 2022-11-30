"""Franchise serializers."""

from elites_retail_portal.common.serializers import BaseSerializerMixin
from elites_retail_portal.enterprises import models

from rest_framework.fields import ReadOnlyField


class EnterpriseSerializer(BaseSerializerMixin):
    """Enterprise Serialiazer class."""

    class Meta:
        """Meta class for Enterprise viewset."""

        model = models.Enterprise
        fields = '__all__'


class StaffSerializer(BaseSerializerMixin):
    """Staff Serialiazer class."""

    full_name = ReadOnlyField()

    class Meta:
        """Meta class for Staff viewset."""

        model = models.Staff
        fields = '__all__'
