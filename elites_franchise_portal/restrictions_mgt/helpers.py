"""."""
from elites_franchise_portal.enterprises.models import Enterprise
from elites_franchise_portal.restrictions_mgt.models import EnterpriseSetupRules

def get_valid_enterprise_setup_rules(enterpise_code):
    enterprise_setup_rules = EnterpriseSetupRules.objects.get(
        enterprise=enterpise_code, is_active=True)
    return enterprise_setup_rules
