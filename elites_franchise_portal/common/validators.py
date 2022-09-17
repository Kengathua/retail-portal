"""Common validators."""

import re
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

phoneNumberRegex = RegexValidator(regex=r"^\+?1?\d{8,15}$")


def franchise_enterprise_code_validator(code):
    """Validate franchise code."""
    enterprise_code_pattern = "[A-Z]+-+[A-Z]+/+[A-Z]+-+[A-Z]+/+[0-9]+-+[0-9]"

    if not (re.search(enterprise_code_pattern, code)):
        raise ValidationError([{
            'elites code': 'Please use a valid elites code format for example EAG-F/EAS-MB/22001-01'    # noqa
        }])

    return True


def items_enterprise_code_validator(code):
    """Validate Item code."""
    items_code_pattern = "[A-Z]+-+[A-Z]+/+[A-Z]+-+[A-Z]+/+[0-9]"

    if not (re.search(items_code_pattern, code)):
        raise ValidationError([{
            'elites code': 'Please use a valid elites code format for example EAG-F/EAS-MB/22001-01'    # noqa
        }])

    return True


def units_enterprise_code_validator(code):
    """Validate Units code."""
    items_code_pattern = "[A-Z]+-+[A-Z]+/+[A-Z]+-+[0-9|A-Z]+/+[0-9]"

    if not (re.search(items_code_pattern, code)):
        raise ValidationError([{
            'elites code': 'Please use a valid elites code format for example EAG-F/EAS-MB/22001-01'    # noqa
        }])

    return True
