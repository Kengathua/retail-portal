"""Restriction Rules views file."""

from elites_franchise_portal.common.views import BaseViewMixin

from elites_franchise_portal.enterprise_mgt import serializers
from elites_franchise_portal.enterprise_mgt.models import (
    EnterpriseSetup, EnterpriseSetupRules)


class EnterpriseSetupViewSet(BaseViewMixin):
    """EnterpriseSetup ViewSet class."""

    queryset = EnterpriseSetup.objects.all()
    serializer_class = serializers.EnterpriseSetupSerializer


class EnterpriseSetupRulesViewSet(BaseViewMixin):
    """EnterpriseSetupRules ViewSet class."""

    queryset = EnterpriseSetupRules.objects.all()
    serializer_class = serializers.EnterpriseSetupRulesSerializer
