"""Common utilities file."""

from django.core.exceptions import ValidationError


def validate_enterprise_exists(code):
    """Validate enterprise exists."""
    from elites_retail_portal.enterprises.models import Enterprise
    enterprise_exists = Enterprise.objects.filter(enterprise_code=code).exists()
    if not enterprise_exists:
        raise ValidationError([{
            'enterprise': f'Enterprise with enterprise code {code} does not exist'
        }])
