"""Franchise serializers."""

from elites_franchise_portal.common.serializers import BaseSerializerMixin
from elites_franchise_portal.enterprises import models

from rest_framework.fields import CharField


class EnterpriseSerializer(BaseSerializerMixin):
    """Enterprise Serialiazer class."""

    class Meta:
        """Meta class for Enterprise viewset."""

        model = models.Enterprise
        fields = '__all__'
