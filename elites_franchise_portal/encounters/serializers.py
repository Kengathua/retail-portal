"""Encounter models serializers file."""

from elites_franchise_portal.common.serializers import BaseSerializerMixin
from elites_franchise_portal.encounters import models


class EncounterSerializer(BaseSerializerMixin):
    """Encounter serializer class."""

    class Meta:
        """Encounter Meta class."""

        model = models.Encounter
        fields = '__all__'
