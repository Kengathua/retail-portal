"""Custom permissions file."""

from rest_framework import permissions


class DRFScreenPermission(permissions.BasePermission):
    """Screen Permission."""

    edit_methods = ("PUT", "PATCH")

    def has_permission(self, request, view):
        """Check if user has the required permissions."""
        user_permissions = list(request.user.permissions)
        try:
            if not set(view.required_permissions).issubset(set(user_permissions)):
                return False

        except AttributeError:
            pass

        if request.user.is_authenticated:
            return True

    def has_object_permission(self, request, view, obj):
        """."""
        if request.user.is_superuser:
            return True

        if request.method in permissions.SAFE_METHODS:
            return True

        if obj.author == request.user:
            return True

        if request.user.is_staff and request.method not in self.edit_methods:
            return True

        return False
