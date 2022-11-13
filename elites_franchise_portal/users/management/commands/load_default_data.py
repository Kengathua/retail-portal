"""Load default data command."""
import uuid

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from elites_franchise_portal.enterprises.models import Enterprise
from elites_franchise_portal.users.perms import BASE_PERMISSIONS_MAPPER
from elites_franchise_portal.users.roles import BASE_ROLES_MAPPER
from elites_franchise_portal.users.models import (
    Permission, Role, UserRole, Group, GroupPermission)


class Command(BaseCommand):
    """."""

    help = 'Sets up the default roles and permissions data'

    def add_arguments(self, parser):
        """."""
        pass

    def handle(self, *args, **options):
        """."""
        enterprise = Enterprise.objects.filter(enterprise_code='EAL-E/EA-MB/2201-01').first()
        if not enterprise:
            enterprise = Enterprise.objects.create(
                name='Elites Age', enterprise_code='EAL-E/EA-MB/2201-01',
                updated_by=uuid.uuid4(), created_by=uuid.uuid4())

        user = get_user_model().objects.filter(email='adminuser@email.com').first()
        if not user:
            user = get_user_model().objects.create_superuser(
                    email='adminuser@email.com', first_name='Admin', last_name='User',
                    guid=uuid.uuid4(), password='Hu46!YftP6^l$',
                    enterprise=enterprise.enterprise_code)

        audit_fields = {
            'created_by': user.id,
            'updated_by': user.id,
            'enterprise': user.enterprise
        }
        super_admin_group = Group.objects.filter(
            name='Super Admin Group', enterprise=user.enterprise).first()
        if not super_admin_group:
            super_admin_group = Group.objects.create(name='Super Admin Group', **audit_fields)

        for key, value in BASE_ROLES_MAPPER.items():
            role = Role.objects.filter(name=key, value=value).first()
            if not role:
                try:
                    role = Role.objects.create(name=key, value=value)
                except Exception as exc:
                    raise CommandError(str(exc))

            if not UserRole.objects.filter(user=user, role=role).exists():
                UserRole.objects.create(user=user, role=role)

        for key, value in BASE_PERMISSIONS_MAPPER.items():
            perm = Permission.objects.filter(name=key, value=value).first()
            if not perm:
                perm = Permission.objects.create(name=key, value=value)

            if not GroupPermission.objects.filter(
                    group=super_admin_group, permission=perm).exists():
                GroupPermission.objects.create(
                    group=super_admin_group, permission=perm, **audit_fields)

        self.stdout.write(self.style.SUCCESS('Successfully loaded the default data'))
