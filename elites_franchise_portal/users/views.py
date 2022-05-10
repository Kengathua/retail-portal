"""Users views file."""

from rest_framework import viewsets
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from elites_franchise_portal.users.models import User
from elites_franchise_portal.users.serializers import UserSerializer, MeSerializer


class UserViewSet(viewsets.ModelViewSet):
    """User Viewset class."""

    queryset = User.objects.all()
    serializer_class = UserSerializer


class MeView(RetrieveAPIView):
    """Return the details of the currently logged in user."""

    permission_classes = (IsAuthenticated,)
    queryset = User.objects.none()
    serializer_class = MeSerializer

    def get_object(self):
        """Limit this view to only return the logged in user's details."""
        return self.request.user
