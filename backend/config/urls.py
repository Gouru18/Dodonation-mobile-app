from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from donations.views import DonationViewSet
from meetings.views import MeetingViewSet
from donations.views import RequestOTPView

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'donations', DonationViewSet)
router.register(r'meetings', MeetingViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    # The API URLs are now determined automatically by the router.
    path('api/', include(router.urls)), 
    path('api/request-otp/', RequestOTPView.as_view(), name='request-otp'),
]