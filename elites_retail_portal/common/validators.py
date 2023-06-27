"""Common validators."""

import re
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

phoneNumberRegex = RegexValidator(regex=r"^\+?1?\d{8,15}$")


def enterprise_enterprise_code_validator(code):
    """Validate enterprise code."""
    enterprise_code_pattern = "[A-Z]+-+[A-Z]+/+[A-Z]+-+[A-Z]+/+[0-9]+-+[0-9]"

    if not (re.search(enterprise_code_pattern, code)):
        msg = 'Please use a valid enterprise code format '\
            'for example EAG-F/EAS-MB/23001-01 or leave the field blank'
        raise ValidationError([{
            'elites_code': msg  # noqa
        }])

    return True


def items_enterprise_code_validator(code):
    """Validate Item code."""
    items_code_pattern = "[A-Z]+-+[A-Z]+/+[A-Z]+-+[A-Z]+/+[0-9]"

    if not (re.search(items_code_pattern, code)):
        raise ValidationError([{
            'elites_code': 'Please use a valid elites code format for example EAG-F/EAS-MB/23001-01'    # noqa
        }])

    return True


def units_enterprise_code_validator(code):
    """Validate Units code."""
    items_code_pattern = "[A-Z]+-+[A-Z]+/+[A-Z]+-+[0-9|A-Z]+/+[0-9]"

    if not (re.search(items_code_pattern, code)):
        raise ValidationError([{
            'elites_code': 'Please use a valid elites code format for example EAG-F/EAS-MB/23001-01'    # noqa
        }])

    return True
