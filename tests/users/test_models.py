import uuid

from django.test import TestCase
from elites_franchise_portal.users.models import User
from django.contrib.auth.models import Group

from model_bakery import baker

class TestUser(TestCase):

    def test_create_user(self):
        user = User.objects.create(
            email='user@email.com', first_name='Test', last_name='User', guid=uuid.uuid4())
        user.save()

        group = baker.make(Group, name='Group One')
        user.groups.add(group)
        user.save()

        assert user.groups.get().name == group.name == 'Group One'
        assert user.groups.all() != []
        assert user.user_permissions.all() != []


    def test_create_superuser(self):
        super_user = User.objects.create_superuser(
            email='user@email.com', first_name='Test', last_name='User', guid=uuid.uuid4())
        assert super_user
        assert super_user.is_staff == True
        assert super_user.is_admin == True
        assert super_user.is_superuser == True
