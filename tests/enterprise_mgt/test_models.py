"""."""

import pytest

from django.test import TestCase
from django.core.exceptions import ValidationError

from elites_retail_portal.enterprises.models import Enterprise
from elites_retail_portal.debit.models import Inventory
from elites_retail_portal.catalog.models import Catalog
from elites_retail_portal.warehouses.models import Warehouse
from elites_retail_portal.enterprise_mgt.models import (
    EnterpriseSetupRule, EnterpriseSetupRuleWarehouse,
    EnterpriseSetupRuleCatalog, EnterpriseSetupRuleInventory)

from model_bakery import baker
from model_bakery.recipe import Recipe

class TestEnterpriseSetupRule(TestCase):
    """."""

    def setUp(self) -> None:
        self.enterprise = baker.make(
            Enterprise, name='Enterprise One', enterprise_code='EAL-E/EO-MB/2301-01',
            enterprise_type='FRANCHISE', business_type='SHOP')
        enterprise_code = self.enterprise.enterprise_code
        inventory = baker.make(
            Inventory, inventory_name='Elites Age Supermarket Available Inventory',
            is_default=True, is_master=True,
            is_active=True, inventory_type='AVAILABLE', enterprise=enterprise_code)
        catalog = baker.make(
            Catalog, catalog_name='Elites Age Supermarket Standard Catalog',
            is_default=True,
            description='Standard Catalog', is_standard=True, enterprise=enterprise_code)
        warehouse = baker.make(
            Warehouse, warehouse_name='Elites Private Warehouse', is_default=True,
            is_receiving=True, enterprise=enterprise_code)
        self.rule = baker.make(
            EnterpriseSetupRule, name='Elites Age', is_active=True, enterprise=enterprise_code)
        baker.make(
            EnterpriseSetupRuleInventory, rule=self.rule, inventory=inventory,
            enterprise=enterprise_code)
        baker.make(
            EnterpriseSetupRuleWarehouse, rule=self.rule, warehouse=warehouse,
            enterprise=enterprise_code)
        baker.make(
            EnterpriseSetupRuleCatalog, rule=self.rule, catalog=catalog,
            enterprise=enterprise_code)

        return super().setUp()

    def test_validate_unique_rule(self):
        """."""
        enterprise_code = self.enterprise.enterprise_code
        rule_recipe = Recipe(
                EnterpriseSetupRule, name='Another rule for Elites Age',
                is_active=True, enterprise=enterprise_code)
        with pytest.raises(ValidationError) as ve:
            rule_recipe.make()
        msg = 'A rule for this enterprise already exists. Please deactivate or update the exisiting rule to continue'   # noqa
        assert msg in ve.value.messages

        self.rule.is_active = False
        self.rule.save()

        rule_recipe.make()
        assert EnterpriseSetupRule.objects.count() == 2
