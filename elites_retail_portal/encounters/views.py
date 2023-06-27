"""Encounter Views file."""

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from elites_retail_portal.common.views import BaseViewMixin
from elites_retail_portal.encounters.models import Encounter
from elites_retail_portal.encounters import serializers, filters
from elites_retail_portal.encounters.tasks import (process_customer_encounter)


class EncounterViewSet(BaseViewMixin):
    """Sale View class."""

    queryset = Encounter.objects.all()
    serializer_class = serializers.EncounterSerializer
    filterset_class = filters.EncounterFilter
    search_fields = (
        'submitted_amount', 'payable_amount', 'balance_amount', 'total_deposit',
        'processing_status', 'stalling_reason', 'note', 'receipt_number',
        'encounter_number', 'served_by__title', 'sales_person__title',
        'served_by__first_name', 'served_by__last_name', 'served_by__other_names',
        'sales_person__first_name', 'sales_person__last_name', 'sales_person__other_names',
        'customer__title', 'customer__first_name', 'customer__last_name', 'customer__other_names'
    )
    required_permissions = [
        'encounters.add_encounter',
        'encounters.change_encounter',
        'encounters.delete_encounter',
        'encounters.view_encounter',
    ]

    @action(methods=['post'], detail=True)
    def process_encounter(self, request, *args, **kwargs):
        """Activate item end point."""
        encounter = self.get_object()
        process_customer_encounter(encounter.id)

        return Response(data={"status": "OK"}, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True)
    def cancel_receipt(self, request, *args, **kwargs):
        """Activate item end point."""
        encounter = self.get_object()
        note = self.request.data.get('note', None)
        encounter.cancel_receipt(note)
        data = serializers.EncounterSerializer(encounter).data

        return Response(data=data, status=status.HTTP_200_OK)
