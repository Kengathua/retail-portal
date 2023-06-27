import uuid

from django.test import TestCase
from elites_retail_portal.users.models import User, Group
from elites_retail_portal.enterprises.models import Enterprise

from model_bakery import baker


class TestUser(TestCase):

    def test_create_user(self):
        franchise = baker.make(Enterprise, name='Elites Age Supermarket')
        enterprise_code = franchise.enterprise_code
        group = baker.make(Group, name='Group One', enterprise=enterprise_code)
        user = User.objects.create(
            email='user@email.com', group=group, first_name='Test', last_name='User', guid=uuid.uuid4())
        user.save()

        user.group= group
        user.save()
        
        assert user
        assert user.group

        # assert user.groups.get().name == group.name == 'Group One'
        # assert user.groups.all() != []
        # assert user.user_permissions.all() != []


    def test_create_superuser(self):
        super_user = User.objects.create_superuser(
            email='user@email.com', first_name='Test', last_name='User', guid=uuid.uuid4())
        assert super_user
        assert super_user.is_staff == True
        assert super_user.is_admin == True
        assert super_user.is_superuser == True
