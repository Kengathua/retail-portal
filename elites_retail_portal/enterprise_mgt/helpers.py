"""."""

from elites_retail_portal.enterprise_mgt.models import EnterpriseSetupRule


def get_valid_enterprise_setup_rules(enterpise_code):
    """Get the valid enterprise setup rule for the enterprise."""
    enterprise_setup_rules = EnterpriseSetupRule.objects.filter(
        enterprise=enterpise_code, is_active=True).first()
    return enterprise_setup_rules
