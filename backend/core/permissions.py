from rest_framework import permissions


class IsDonor(permissions.BasePermission):
    """Permission to check if user is a donor"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'donor'


class IsNGO(permissions.BasePermission):
    """Permission to check if user is an NGO"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'ngo'


class IsAdminUser(permissions.BasePermission):
    """Permission to check if user is admin"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff


class IsOwnerOrAdmin(permissions.BasePermission):
    """Permission to check if user is owner of object or admin"""
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.user == request.user


class IsDonationOwner(permissions.BasePermission):
    """Permission to check if user is owner of donation"""
    def has_object_permission(self, request, view, obj):
        return obj.donor == request.user


class IsClaimInvolved(permissions.BasePermission):
    """Permission to check if user is involved in claim (donor or ngo)"""
    def has_object_permission(self, request, view, obj):
        return (
            obj.donation.donor == request.user or
            obj.receiver == request.user
        )


class IsMeetingInvolved(permissions.BasePermission):
    """Permission to check if user is involved in meeting"""
    def has_object_permission(self, request, view, obj):
        return (
            obj.claim_request.donation.donor == request.user or
            obj.claim_request.receiver == request.user
        )
