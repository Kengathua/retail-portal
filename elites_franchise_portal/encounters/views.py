"""Encounter Views file."""

from elites_franchise_portal.common.views import BaseViewMixin
from elites_franchise_portal.encounters.models import Encounter
from elites_franchise_portal.encounters import serializers


class EncounterViewSet(BaseViewMixin):
    """Sale View class."""

    queryset = Encounter.objects.all()
    serializer_class = serializers.EncounterSerializer
