"""User serializers file."""

from rest_framework.fields import ReadOnlyField, SerializerMethodField, CharField
from rest_framework.serializers import ModelSerializer

from elites_retail_portal.users.models import User
from elites_retail_portal.enterprises.models import Enterprise


class UserSerializer(ModelSerializer):
    """Serialize a user, their roles and their permissions."""

    full_name = ReadOnlyField(source='get_full_name', read_only=True)
    roles = CharField(source='user_roles')
    permissions = ReadOnlyField()

    class Meta:
        """Exclude sensitive fields (e.g password) from being serialized for a user."""

        model = User
        fields = (
            'id', 'first_name', 'last_name', 'other_names',
            'full_name', 'phone_no', 'email', 'date_of_birth',
            'date_joined', 'is_staff', 'is_admin', 'is_active',
            'guid', 'roles', 'permissions', 'enterprise', 'updated_on',)


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
