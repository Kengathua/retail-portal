import uuid
import pytest
from functools import partial

from django.contrib.auth import get_user_model

from rest_framework.test import APIClient

from elites_franchise_portal.users.models import User
from elites_franchise_portal.franchises.models import Franchise

from model_bakery import baker

pytestmark = pytest.mark.django_db

class LoggedInMixin:
    """."""

    def setUp(self):
        """."""
        franchise = baker.make(
            Franchise, name='Franchise One', elites_code='EAL-F/FO-MB/2201-01',
            partnership_type='SHOP')
        user = get_user_model().objects.filter(email='user@email.com')
        if user.exists():
            self.user = user.first()
        else:
            self.user = get_user_model().objects.create_superuser(
                email='user@email.com', first_name='Test', last_name='User', guid=uuid.uuid4(),
                password='Testpass254$', franchise=franchise.elites_code)

        assert self.client.login(username='user@email.com', password='Testpass254$') is True

        headers = self.extra_headers()
        self.client.get = partial(self.client.get, **headers)
        self.client.patch = partial(self.client.patch, **headers)
        self.client.post = partial(self.client.post, **headers)
        self.client.put = partial(self.client.put, **headers)

        return super(LoggedInMixin, self).setUp()

    def extra_headers(self):
        """."""
        return {}


def authenticate_test_user():
    """Authenticate a user for a test."""
    client = APIClient()
    try:
        franchise = Franchise.objects.get(elites_code='EAL-F/FO-MB/2201-01')
    except Franchise.DoesNotExist:
        franchise = baker.make(
            Franchise, name='Franchise One', elites_code='EAL-F/FO-MB/2201-01',
            partnership_type='SHOP')
    users = get_user_model().objects.filter(email='testuser@email.com')
    if users.exists():
        user = users.first()
    else:
        user = get_user_model().objects.create_superuser(
            email='testuser@email.com', first_name='Test', last_name='User',
            guid=uuid.uuid4(), password='Testpass254$', franchise=franchise.elites_code)
    client.force_authenticate(user)

    return client
