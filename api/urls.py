from django.urls import path
from . import views    


urlpatterns = [
    # Test endpoint
    path('test/', views.test, name='test'),
    
    # User authentication endpoints
    path('users/login/', views.login, name='api-login'),
    path('users/select-role/', views.selct_role, name='api-select-role'),
    
    # NGO profile endpoints
    path('ngo/signup/', views.create_ngo_profile, name='ngo-signup'),
    path('ngo/profile/', views.get_ngo_profiles, name='ngo-profile-list'),
    path('ngo/profile/<int:pk>/', views.ngo_profile_detail, name='ngo-profile-detail'),
    
    # Donor profile endpoints
    path('donor/signup/', views.create_donor_profile, name='donor-signup'),
    path('donor/profile/', views.get_donor_profiles, name='donor-profile-list'), #semi-ok, not loading NGOs list
    path('donor/profile/<int:pk>/', views.donor_profile_detail, name='donor-profile-detail'),
    
    # Donation endpoints
    path('core/donations/', views.get_donations, name='donations-list'), #ok
    path('core/donations/create/', views.create_donation, name='create-donation'),
    path('core/donations/<int:pk>/', views.donation_detail, name='donation-detail'),
    
    # Claim request endpoints
    path('core/claim-requests/', views.get_claim_requests, name='claim-requests-list'),
    path('core/claim-requests/create/', views.create_claim_request, name='create-claim-request'), #ok
    path('core/claim-requests/<int:pk>/', views.claim_request_detail, name='claim-request-detail'),
    
    # General review endpoints
    path('core/general-reviews/', views.get_general_reviews, name='general-reviews-list'), #ok
    path('core/general-reviews/create/', views.create_general_review, name='create-general-review'), #ok
    path('core/general-reviews/<int:pk>/', views.general_review_detail, name='general-review-detail'),
    
    # Report endpoints
    path('core/reports/', views.get_reports, name='reports-list'),
    path('core/reports/create/', views.create_report, name='create-report'), #ok
    path('core/reports/<int:pk>/', views.report_detail, name='report-detail'),
]

