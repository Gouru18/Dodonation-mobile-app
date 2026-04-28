from rest_framework import permissions
from ngo.models import NGOProfile
from donor.models import DonorProfile


class IsLoggedIn(permissions.BasePermission):
    """
    Allows access only to authenticated users (NGO or Donor).
    Excludes admin users.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role in ['ngo', 'donor']


class IsLoggedInOrReadOnly(permissions.BasePermission):
    """
    Allows authenticated users (NGO or Donor) to create/edit objects. 
    Others can only read.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and request.user.role in ['ngo', 'donor']


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


class IsNGOOwner(permissions.BasePermission):
    """
    Allows access only if the user is the NGO that owns the object.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.role != 'ngo':
            return False
        
        try:
            ngo_profile = NGOProfile.objects.get(user=request.user)
            # Check if the NGO owns the claim request
            if hasattr(obj, 'receiver'):
                return obj.receiver == ngo_profile
            return False
        except NGOProfile.DoesNotExist:
            return False


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


class IsDonorOwner(permissions.BasePermission):
    """
    Allows access only if the user is the Donor that owns the object.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.role != 'donor':
            return False
        
        try:
            donor_profile = DonorProfile.objects.get(user=request.user)
            # Check if the Donor owns the donation
            if hasattr(obj, 'donor'):
                return obj.donor == donor_profile
            return False
        except DonorProfile.DoesNotExist:
            return False