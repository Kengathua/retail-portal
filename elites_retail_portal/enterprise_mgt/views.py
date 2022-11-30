"""Restriction Rules views file."""

from elites_retail_portal.common.views import BaseViewMixin

from elites_retail_portal.enterprise_mgt import serializers
from elites_retail_portal.enterprise_mgt.models import (
    EnterpriseSetup, EnterpriseSetupRule, EnterpriseSetupRuleInventory, EnterpriseSetupRuleWarehouse, EnterpriseSetupRuleCatalog)


class EnterpriseSetupViewSet(BaseViewMixin):
    """EnterpriseSetup ViewSet class."""

    queryset = EnterpriseSetup.objects.all()
    serializer_class = serializers.EnterpriseSetupSerializer


class EnterpriseSetupRuleViewSet(BaseViewMixin):
    """EnterpriseSetupRule ViewSet class."""

    queryset = EnterpriseSetupRule.objects.all()
    serializer_class = serializers.EnterpriseSetupRuleSerializer


class EnterpriseSetupRuleInventoryViewSet(BaseViewMixin):
    """EnterpriseSetupRule Inventory ViewSet class."""

    queryset = EnterpriseSetupRuleInventory.objects.all()
    serializer_class = serializers.EnterpriseSetupRuleInventorySerializer


class EnterpriseSetupRuleWarehouseViewSet(BaseViewMixin):
    """EnterpriseSetupRule Warehouse ViewSet class."""

    queryset = EnterpriseSetupRuleWarehouse.objects.all()
    serializer_class = serializers.EnterpriseSetupRuleWarehouseSerializer


class EnterpriseSetupRuleCatalogViewSet(BaseViewMixin):
    """EnterpriseSetupRule Catalog ViewSet class."""

    queryset = EnterpriseSetupRuleCatalog.objects.all()
    serializer_class = serializers.EnterpriseSetupRuleCatalogSerializer
