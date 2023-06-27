import uuid
import pytest
from functools import partial

from django.contrib.auth import get_user_model

from rest_framework.test import APIClient

from elites_retail_portal.users.models import (
    Role, Group, GroupPermission, UserRole, Permission)
from elites_retail_portal.enterprises.models import Enterprise
from elites_retail_portal.users.perms import BASE_PERMISSIONS_MAPPER
from elites_retail_portal.users.roles import BASE_ROLES_MAPPER

from model_bakery import baker

pytestmark = pytest.mark.django_db

class LoggedInMixin:
    """."""

    def setUp(self):
        """."""
        enterprise = baker.make(
            Enterprise, name='Enterprise One', enterprise_code='EAL-E/EO-MB/2301-01',
            enterprise_type='FRANCHISE', business_type='SHOP')
        user = get_user_model().objects.filter(email='user@email.com')
        if user.exists():
            self.user = user.first()
        else:
            self.user = get_user_model().objects.create_superuser(
                email='user@email.com', first_name='Test', last_name='User', guid=uuid.uuid4(),
                password='Testpass254$', enterprise=enterprise.enterprise_code)

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
        enterprise = Enterprise.objects.get(enterprise_code='EAL-E/EO-MB/2301-01')
    except Enterprise.DoesNotExist:
        enterprise = baker.make(
            Enterprise, name='Enterprise One', enterprise_code='EAL-E/EO-MB/2301-01',
            enterprise_type='FRANCHISE', business_type='SHOP')
    users = get_user_model().objects.filter(email='testuser@email.com')
    if users.exists():
        user = users.first()
    else:
        user = get_user_model().objects.create_superuser(
            email='testuser@email.com', first_name='Test', last_name='User',
            guid=uuid.uuid4(), password='Testpass254$', enterprise=enterprise.enterprise_code)

    audit_fields = {
        'created_by': user.id,
        'updated_by': user.id,
        'enterprise': user.enterprise
    }
    super_admin_group = Group.objects.filter(
        name='Super Admin Group', enterprise=user.enterprise).first()
    if not super_admin_group:
        super_admin_group = Group.objects.create(name='Super Admin Group', **audit_fields)

    user.group = super_admin_group
    user.save()

    for key, value in BASE_ROLES_MAPPER.items():
        role = Role.objects.filter(name=key, value=value).first()
        if not role:
            try:
                role = baker.make(Role, name=key, value=value)
            except Exception as exc:
                return

        if not UserRole.objects.filter(user=user, role=role).exists():
            UserRole.objects.create(user=user, role=role)

    for key, value in BASE_PERMISSIONS_MAPPER.items():
        perm = Permission.objects.filter(name=key, value=value).first()
        if not perm:
            perm = baker.make(Permission, name=key, value=value)

        if not GroupPermission.objects.filter(
                group=super_admin_group, permission=perm).exists():
            GroupPermission.objects.create(
                group=super_admin_group, permission=perm, **audit_fields)

    client.force_authenticate(user)

    return client
