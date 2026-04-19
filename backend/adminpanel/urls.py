from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AdminClaimRequestViewSet,
    AdminDashboardViewSet,
    AdminDonationViewSet,
    AdminDonorProfileViewSet,
    AdminMeetingViewSet,
    AdminNGOPermitViewSet,
    AdminNGOProfileViewSet,
    AdminOTPCodeViewSet,
    AdminUserViewSet,
)

router = DefaultRouter()
router.register(r'dashboard', AdminDashboardViewSet, basename='admin-dashboard')
router.register(r'users', AdminUserViewSet, basename='admin-users')
router.register(r'otp-codes', AdminOTPCodeViewSet, basename='admin-otp-codes')
router.register(r'donor-profiles', AdminDonorProfileViewSet, basename='admin-donor-profiles')
router.register(r'ngo-profiles', AdminNGOProfileViewSet, basename='admin-ngo-profiles')
router.register(r'permits', AdminNGOPermitViewSet, basename='admin-permits')
router.register(r'donations', AdminDonationViewSet, basename='admin-donations')
router.register(r'claims', AdminClaimRequestViewSet, basename='admin-claims')
router.register(r'meetings', AdminMeetingViewSet, basename='admin-meetings')

urlpatterns = [
    path('', include(router.urls)),
]
