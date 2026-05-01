from rest_framework import permissions
from ngo.models import NGOProfile
from donor.models import DonorProfile


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


class IsNGOOrReadOnly(permissions.BasePermission):
    """
    Allows NGOs to create/edit objects. Others can only read.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and request.user.role == 'ngo'


class IsDonor(permissions.BasePermission):
    """
    Allows access only to authenticated Donor users.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role == 'donor'


class IsDonorOrReadOnly(permissions.BasePermission):
    """
    Allows Donors to create/edit objects. Others can only read.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and request.user.role == 'donor'
