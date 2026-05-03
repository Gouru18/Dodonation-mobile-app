from rest_framework import permissions

class IsLoggedIn(permissions.BasePermission):
    """
    Allows access only to authenticated users (NGO or Donor).
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role in ['ngo', 'donor']


class IsNGO(permissions.BasePermission):
    """
    Allows access only to authenticated NGO users.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role == 'ngo'


class IsDonor(permissions.BasePermission):
    """
    Allows access only to authenticated Donor users.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role == 'donor'


