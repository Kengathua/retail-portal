"""Franchise views."""

from elites_franchise_portal.common.views import BaseViewMixin
from elites_franchise_portal.enterprises.models import (
    Enterprise, EnterpriseContact, Platform)
from elites_franchise_portal.enterprises import serializers
from elites_franchise_portal.enterprises import filters

class EnterpriseViewSet(BaseViewMixin):
    """Enterprise ViewSet."""

    queryset = Enterprise.objects.all()
    serializer_class = serializers.EnterpriseSerializer
    filterset_class = filters.EnterpriseFilter
    search_fields = (
        'name', 'enterprise_code', 'reg_no', 'enterprise_type')
