from django.urls import path
from . import views    

urlpatterns = [
    path('core/donations/', views.get_donations, name='donations-list'),
    path('core/claim-requests/', views.get_claim_requests, name='claim-requests-list'),
    path('core/general-reviews/', views.get_general_reviews, name='general-reviews-list'),
    path('core/reports/', views.get_reports, name='reports-list'),
    path('core/donations/create/', views.create_donation, name='create-donation'),
    path('core/claim-requests/create/', views.create_claim_request, name='create-claim-request'),
    path('core/general-reviews/create/', views.create_general_review, name='create-general-review'),
    path('core/reports/create/', views.create_report, name='create-report'),
    path('ngo/signup/', views.create_ngo_profile, name='ngo-signup'),
    path('donor/signup/', views.create_donor_profile, name='donor-signup'),
    path('ngo/profile/', views.get_ngo_profiles, name='ngo-profile'),
    path('donor/profile/', views.get_donor_profiles, name='donor-profile'),
    path('users/login/', views.login, name='api-login'),
    path('users/select-role/', views.selct_role, name='api-select-role'),
    path('test/', views.test, name='test'),
]