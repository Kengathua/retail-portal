"""."""

import pytest
from django.test import TestCase
from django.core.exceptions import ValidationError

from elites_franchise_portal.enterprises.models import Enterprise

from model_bakery import baker
from model_bakery import recipe


class TestEnterprise(TestCase):
    """."""

    def test_create_franchise(self):
        """."""
        enterprise1 = baker.make(Enterprise, name='Franchise Number One')
        assert enterprise1.enterprise_code == 'EAL-E/FNO-MB/2201-01'
        enterprise2 = baker.make(Enterprise, name='Franchise Number One')
        assert enterprise2.enterprise_code == 'EAL-E/FNO-MB/2202-01'

        assert enterprise1.enterprise_code != enterprise2.enterprise_code

    def test_validate_franchise_entries(self):
        """."""
        franchise = recipe.Recipe(
            Enterprise, name='Franchise Number One', is_main_branch=False)
        with pytest.raises(ValidationError) as ve:
            franchise.make()

        msg = 'Missing main branch. Please add the code of the main branch'
        assert msg in ve.value.messages

        with pytest.raises(ValidationError) as ve:
            franchise.make(main_branch_code='0000')
        msg = 'Mismatching main branch details. Please add a valid main branch code'
        assert msg in ve.value.messages

        baker.make(Enterprise, name='Franchise Number One')
        franchise.make(main_branch_code='EAL-E/FNO-MB/2201-01')
        assert franchise

    def test_fail_is_main_branch_and_has_main_code_attached(self):
        """."""
        franchise = recipe.Recipe(
            Enterprise, name='Franchise Number One', is_main_branch=True,
            main_branch_code='0000')
        with pytest.raises(ValidationError) as ve:
            franchise.make()

        msg = 'The franchise is marked as a main branch. '\
            'Please remove the main branch code attached to it'
        assert msg in ve.value.messages
