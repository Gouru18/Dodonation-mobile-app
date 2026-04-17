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
from django.http import JsonResponse
from django.urls import path, include

def api_root(request):
    return JsonResponse({
        'status': 'ok',
        'message': 'API is running; use /api/auth/ and /api/profiles/',
    })

urlpatterns = [
    path('', api_root, name='api-root'),
    path('admin/', admin.site.urls),
    # The API URLs are now determined automatically by the router.
    path('api/', include(router.urls)), 
    path('api/request-otp/', RequestOTPView.as_view(), name='request-otp'),
    path('api/auth/', include('accounts.urls')),
    path('api/profiles/', include('profiles.urls')),
]

# That gives endpoints like:/api/auth/register/,/api/auth/login/,/api/auth/verify-otp/,/api/auth/token/refresh/,/api/profiles/donor/<id>/,/api/profiles/ngo/<id>/