import pytest
from django.core.exceptions import ValidationError
from elites_retail_portal.common.validators import enterprise_enterprise_code_validator


def test_enterprise_enterprise_code_validator():
    code = "EAL-F/FNO-MB/2301-01"
    assert enterprise_enterprise_code_validator(code)


def test_enterprise_enterprise_code_validator_fail():
    code = "000-F/FNO-MB/2301-01"
    with pytest.raises(ValidationError) as ve:
        enterprise_enterprise_code_validator(code)

    msg = 'Please use a valid enterprise code format for example EAG-F/EAS-MB/23001-01 or leave the field blank'
    assert msg in ve.value.messages
