import pytest
from django.test import TestCase
from django.core.exceptions import ValidationError

from elites_franchise_portal.franchises.models import Franchise

from model_bakery import baker
from model_bakery import recipe

class TestFranchise(TestCase):

    def test_create_franchise(self):
        franchise1 = baker.make(Franchise, name='Franchise Number One')
        assert franchise1.elites_code == 'EAL-F/FNO-MB/2201-01'
        franchise2 = baker.make(Franchise, name='Franchise Number One')
        assert franchise2.elites_code == 'EAL-F/FNO-MB/2202-01'

        assert franchise1.elites_code != franchise2.elites_code

    def test_validate_franchise_entries(self):
        franchise = recipe.Recipe(Franchise, name='Franchise Number One', is_main=False)
        with pytest.raises(ValidationError) as ve:
            franchise.make()

        msg = 'Missing main branch. Please add the code of the main branch'
        assert msg in ve.value.messages

        with pytest.raises(ValidationError) as ve:
            franchise.make(main_branch_code='0000')
        msg = 'Mismatching main branch details. Please add a valid main branch code'
        assert msg in ve.value.messages

        baker.make(Franchise, name='Franchise Number One')
        franchise.make(main_branch_code='EAL-F/FNO-MB/2201-01')
        assert franchise

    def test_fail_is_main_and_has_main_code_attached(self):
        franchise = recipe.Recipe(Franchise, name='Franchise Number One', is_main=True, main_branch_code='0000')
        with pytest.raises(ValidationError) as ve:
            franchise.make()

        msg = 'The franchise is marked as a main branch. Please remove the main branch code attached to it'
        assert msg in ve.value.messages
