"""Encounters filters file."""

import django_filters
from django.db import models

from elites_franchise_portal.common.filters import SearchComboboxBaseFilter
from elites_franchise_portal.encounters.models import Encounter


class EncounterFilter(SearchComboboxBaseFilter):
    """Filter encounters."""

    class Meta:
        """Restrict filter fields."""

        model = Encounter
        fields = '__all__'
        filter_overrides = {
            models.JSONField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                },
            },
        }
