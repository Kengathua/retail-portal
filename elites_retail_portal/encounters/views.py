"""Encounter Views file."""

from elites_retail_portal.common.views import BaseViewMixin
from elites_retail_portal.encounters.models import Encounter
from elites_retail_portal.encounters import serializers, filters


class EncounterViewSet(BaseViewMixin):
    """Sale View class."""

    queryset = Encounter.objects.all()
    serializer_class = serializers.EncounterSerializer
    filterset_class = filters.EncounterFilter
    required_permissions = [
        'encounters.add_encounter',
        'encounters.change_encounter',
        'encounters.delete_encounter',
        'encounters.view_encounter',
    ]
