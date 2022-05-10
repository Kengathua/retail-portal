"""Franchise views."""

from elites_franchise_portal.common.views import BaseViewMixin
from elites_franchise_portal.franchises.models import (
    Franchise,)
from elites_franchise_portal.franchises import serializers


class FranchiseViewSet(BaseViewMixin):
    """Franchise ViewSet."""

    queryset = Franchise.objects.all()
    serializer_class = serializers.FranchiseSerializer
