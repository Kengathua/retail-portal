"""Restriction Rules views file."""

from elites_franchise_portal.common.views import BaseViewMixin

from elites_franchise_portal.enterprise_mgt import serializers
from elites_franchise_portal.enterprise_mgt.models import (
    EnterpriseSetup, EnterpriseSetupRule)


class EnterpriseSetupViewSet(BaseViewMixin):
    """EnterpriseSetup ViewSet class."""

    queryset = EnterpriseSetup.objects.all()
    serializer_class = serializers.EnterpriseSetupSerializer


class EnterpriseSetupRuleViewSet(BaseViewMixin):
    """EnterpriseSetupRule ViewSet class."""

    queryset = EnterpriseSetupRule.objects.all()
    serializer_class = serializers.EnterpriseSetupRuleSerializer
