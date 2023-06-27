import uuid
import django

django.setup()

from django.contrib.auth import get_user_model
from elites_retail_portal.enterprises.models import Enterprise
from elites_retail_portal.enterprise_mgt.models import (
    EnterpriseSetupRule)
from elites_retail_portal.users.perms import BASE_PERMISSIONS_MAPPER
from elites_retail_portal.users.roles import BASE_ROLES_MAPPER
from elites_retail_portal.users.models import (
    Permission, Role, UserRole, Group, GroupPermission)


enterprise = Enterprise.objects.create(
    name='Elites Supermarket', updated_by=uuid.uuid4(), created_by=uuid.uuid4())
user = get_user_model().objects.filter(email='adminuser@email.com')
if user.exists():
    user = user.first()
else:
    user = get_user_model().objects.create_superuser(
            email='adminuser@email.com', first_name='Admin', last_name='User',
            guid=uuid.uuid4(), password='Hu46!YftP6^l$', enterprise=enterprise.enterprise_code)

audit_fields = {
    'created_by': user.id,
    'updated_by': user.id,
    'enterprise': user.enterprise
}

rule,_ = EnterpriseSetupRule.objects.update_or_create(
    name='Elites Age Supermarket', is_default=True, supports_installment_sales=True,
    is_active=True, **audit_fields)

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
            role = Role.objects.create(name=key, value=value)
        except Exception as exc:
            pass

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
