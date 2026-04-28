from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from donations.views import DonationViewSet, ClaimRequestViewSet
from meetings.views import MeetingViewSet
from django.http import HttpResponse, JsonResponse
import base64

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
        }
    })

def favicon(request):
    favicon_bytes = base64.b64decode(
        'AAABAAEAEBAAAAAAIABoBAAAFgAAACgAAAAQAAAAIAAAAAEABAAAAAAAQAAAAAAAAAAAAAAAAAAAA'
        'AAAAAAAA////AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
    )
    return HttpResponse(favicon_bytes, content_type='image/x-icon')

urlpatterns = [
    path('favicon.ico', favicon),
    path('', api_root, name='api-root'),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/', include('accounts.urls')),
    path('api/admin/', include('adminpanel.urls')),
    path('api/profiles/', include('profiles.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
