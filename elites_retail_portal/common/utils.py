"""Common utilities file."""

from django.core.exceptions import ValidationError


def validate_franchise_exists(code):
    """Validate franchise exists."""
    from elites_retail_portal.enterprises.models import Enterprise
    franchise_exists = Enterprise.objects.filter(enterprise_code=code).exists()
    if not franchise_exists:
        raise ValidationError([{
            'franchise': f'Franchise with franchise code {code} does not exist'
        }])
