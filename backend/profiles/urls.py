from django.urls import path
from .views import DonorProfileDetailView, NGOProfileDetailView

urlpatterns = [
    path('donor/<int:pk>/', DonorProfileDetailView.as_view(), name='donor-profile'),
    path('ngo/<int:pk>/', NGOProfileDetailView.as_view(), name='ngo-profile'),
]