from django.urls import path
from .views import (
    DonorProfileDetailView, NGOProfileDetailView,
    NGOPermitUploadView, NGOPermitListView, NGOPermitApprovalView
)

urlpatterns = [
    path('donor/me/', DonorProfileDetailView.as_view(), name='donor-profile-me'),
    path('ngo/me/', NGOProfileDetailView.as_view(), name='ngo-profile-me'),
    path('permits/upload/', NGOPermitUploadView.as_view(), name='permit-upload'),
    path('permits/', NGOPermitListView.as_view(), name='permit-list'),
    path('permits/<int:pk>/approval/', NGOPermitApprovalView.as_view(), name='permit-approval'),
]