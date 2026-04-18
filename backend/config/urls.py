from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from donations.views import DonationViewSet, ClaimRequestViewSet
from meetings.views import MeetingViewSet
from django.http import JsonResponse

# Create a router and register viewsets
router = DefaultRouter()
router.register(r'donations', DonationViewSet, basename='donation')
router.register(r'claims', ClaimRequestViewSet, basename='claim')
router.register(r'meetings', MeetingViewSet, basename='meeting')

def api_root(request):
    return JsonResponse({
        'status': 'ok',
        'message': 'Dodonation API is running',
        'endpoints': {
            'auth': '/api/auth/',
            'profiles': '/api/profiles/',
            'donations': '/api/donations/',
            'claims': '/api/claims/',
            'meetings': '/api/meetings/',
            'chatbot': '/api/chatbot/',
        }
    })

urlpatterns = [
    path('', api_root, name='api-root'),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/', include('accounts.urls')),
    path('api/profiles/', include('profiles.urls')),
    path('api/chatbot/', include('chatbot.urls')),
]