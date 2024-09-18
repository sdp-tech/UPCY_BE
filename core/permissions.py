from rest_framework.permissions import BasePermission


class IsReformer(BasePermission):
    """
    Allows access only authenticate and "Reformer" users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "reformer")
