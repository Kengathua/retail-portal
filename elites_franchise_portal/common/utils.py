"""Common utilities file."""

from django.core.exceptions import ValidationError


def validate_franchise_exists(code):
    """Validate franchise exists."""
    from elites_franchise_portal.franchises.models import Franchise
    franchise_exists = Franchise.objects.filter(elites_code=code).exists()
    if not franchise_exists:
        raise ValidationError([{
            'franchise': f'Franchise with franchise code {code} does not exist'
        }])
