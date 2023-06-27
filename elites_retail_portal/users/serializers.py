"""User serializers file."""

from rest_framework.fields import ReadOnlyField, SerializerMethodField
from rest_framework.serializers import ModelSerializer

from elites_retail_portal.users.models import (
    User, Group, GroupPermission, Permission)
from elites_retail_portal.enterprises.models import Enterprise
from elites_retail_portal.common.serializers import BaseSerializerMixin


class PermissionSerializer(BaseSerializerMixin):
    """Permissions serializer class."""

    class Meta:
        """Meta class."""

        model = Permission
        fields = '__all__'


class GroupSerializer(BaseSerializerMixin):
    """Group Serializer class."""

    permissions = SerializerMethodField()
    has_perms = SerializerMethodField()

    def get_permissions(self, group):
        """Get all permissions."""
        all_perms = Permission.objects.filter()
        all_perms_ids = list(map(str, Permission.objects.all().values_list('id', flat=True)))
        group_perm_ids = list(map(str, GroupPermission.objects.filter(
            group=group).values_list('permission__id', flat=True)))
        missing_perm_ids = list(set(all_perms_ids) - set(group_perm_ids))
        permissions = []
        if missing_perm_ids:
            perms = Permission.objects.filter(id__in=group_perm_ids)
            for permission in perms:
                data = PermissionSerializer(permission).data
                data['added'] = True
                permissions.append(data)

            missing_perms = Permission.objects.filter(id__in=missing_perm_ids)
            for permission in missing_perms:
                data = PermissionSerializer(permission).data
                data['added'] = False
                permissions.append(data)

            return permissions
        else:
            for permission in all_perms:
                data = PermissionSerializer(permission).data
                data['added'] = True
                permissions.append(data)

            return permissions

    def get_has_perms(self, group):
        """Check if group has permissions."""
        if GroupPermission.objects.filter(group=group).exists():
            return True

        return False

    class Meta:
        """Categories serializer Meta class."""

        model = Group
        fields = '__all__'


class UserSerializer(ModelSerializer):
    """Serialize a user, their roles and their permissions."""

    full_name = ReadOnlyField(source='get_full_name', read_only=True)
    group_name = ReadOnlyField(source='group.name')
    roles = ReadOnlyField(source='user_roles')
    permissions = ReadOnlyField()

    def create(self, validated_data):
        """Create user function."""
        user_payload = {
            "group": validated_data["group"],
            "email": validated_data['email'],
            "first_name": validated_data['first_name'],
            "last_name": validated_data['last_name'],
            "other_names": validated_data['other_names'],
            "phone_no": validated_data['phone_no'],
            "password": validated_data['password'],
            "enterprise": validated_data['enterprise']
        }
        user = User.objects.create_user(**user_payload)
        return user

    class Meta:
        """Exclude sensitive fields (e.g password) from being serialized for a user."""

        model = User
        fields = (
            'id', 'first_name', 'last_name', 'other_names', 'full_name',
            'group', 'group_name', 'phone_no', 'email', 'date_of_birth',
            'date_joined', 'is_staff', 'is_admin', 'is_active', 'password',
            'guid', 'roles', 'permissions', 'enterprise', 'updated_on',)

        extra_kwargs = {
            # 'security_question': {'write_only': True},
            # 'security_question_answer': {'write_only': True},
            'password': {'write_only': True}
        }


class MeSerializer(UserSerializer):
    """A special serializer used to serialize the details of the logged in user."""

    enterprise = SerializerMethodField()

    def get_enterprise(self, user):
        """Serialize details of the business partner that a user is linked to."""
        enterprise = Enterprise.objects.get(enterprise_code=user.enterprise)
        return {
            'id': enterprise.id,
            'name': enterprise.name,
            'enterprise_code': enterprise.enterprise_code
        }

    class Meta(UserSerializer.Meta):
        """Link the MeSerializer to it's parent's Meta."""

        fields = UserSerializer.Meta.fields
