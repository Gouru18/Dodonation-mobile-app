from django.urls import path
from .views import (
    RegisterDonorView, RegisterNGOView, VerifyOTPView,
    LoginView,
    RequestOTPView, CurrentUserView
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/donor/', RegisterDonorView.as_view(), name='register_donor'),
    path('register/ngo/', RegisterNGOView.as_view(), name='register_ngo'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('request-otp/', RequestOTPView.as_view(), name='request_otp'),
    path('me/', CurrentUserView.as_view(), name='current_user'),
]
