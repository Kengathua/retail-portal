"""Franchise serializers."""

from elites_franchise_portal.common.serializers import BaseSerializerMixin
from elites_franchise_portal.franchises import models

from rest_framework.fields import CharField


class FranchiseSerializer(BaseSerializerMixin):
    """Franchise Serialiazer class."""

    elites_code = CharField(read_only=True)

    class Meta:
        """Meta class for franchise viewset."""

        model = models.Franchise
        fields = '__all__'
