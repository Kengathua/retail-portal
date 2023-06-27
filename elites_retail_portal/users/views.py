"""Users views file."""

from rest_framework import viewsets
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from elites_retail_portal.users.models import User, Group
from elites_retail_portal.users.filters import (
    GroupFilter, UserFilter)
from elites_retail_portal.users.serializers import (
    UserSerializer, MeSerializer, GroupSerializer)
from elites_retail_portal.common.views import BaseViewMixin


class GroupViewSet(BaseViewMixin):
    """User Viewset class."""

    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    filterset_class = GroupFilter
    search_fields = (
        'name',)


class UserViewSet(viewsets.ModelViewSet):
    """User Viewset class."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    filterset_class = UserFilter
    search_fields = (
        'id', 'first_name', 'last_name', 'other_names',
        'group__name', 'phone_no', 'email', 'date_of_birth',
        'date_joined', 'guid', 'enterprise',)

    required_permissions = [
        'users.add_user',
        'users.change_user',
        'users.delete_user',
        'users.view_user',
    ]


class MeView(RetrieveAPIView):
    """Return the details of the currently logged in user."""

    permission_classes = (IsAuthenticated,)
    queryset = User.objects.none()
    serializer_class = MeSerializer

    def get_object(self):
        """Limit this view to only return the logged in user's details."""
        return self.request.user
