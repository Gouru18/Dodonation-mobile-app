from django.urls import path
from . import api

urlpatterns = [
    path('login/', api.api_login, name='api_login'),
    path('logout/', api.api_logout, name='api_logout'),
    path('donations/', api.api_donations, name='api_donations'),
    path('requests/', api.api_requests, name='api_requests'),
    path('requests/<int:request_id>/action/', api.api_request_action, name='api_request_action'),
]
