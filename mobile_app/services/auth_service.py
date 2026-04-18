import requests
from utils.config import BASE_URL


class AuthService:
    token = None
    user = None

    @staticmethod
    def register_donor(email, password, full_name, phone=''):
        """Register as a donor"""
        return requests.post(
            f"{BASE_URL}/auth/register/donor/",
            json={
                "email": email,
                "password": password,
                "full_name": full_name,
                "phone": phone
            },
            timeout=10
        )

    @staticmethod
    def register_ngo(email, password, organization_name, phone='', registration_number=''):
        """Register as an NGO"""
        return requests.post(
            f"{BASE_URL}/auth/register/ngo/",
            json={
                "email": email,
                "password": password,
                "organization_name": organization_name,
                "phone": phone,
                "registration_number": registration_number
            },
            timeout=10
        )

    @staticmethod
    def login(email, password):
        """Login with email and password"""
        return requests.post(
            f"{BASE_URL}/auth/login/",
            json={
                "email": email,
                "password": password
            },
            timeout=10
        )

    @staticmethod
    def verify_otp(email, otp):
        """Verify OTP code"""
        return requests.post(
            f"{BASE_URL}/auth/verify-otp/",
            json={
                "email": email,
                "otp": otp
            },
            timeout=10
        )

    @staticmethod
    def request_otp(email):
        """Request new OTP"""
        return requests.post(
            f"{BASE_URL}/auth/request-otp/",
            json={"email": email},
            timeout=10
        )

    @staticmethod
    def get_current_user():
        """Get current user info"""
        return requests.get(
            f"{BASE_URL}/auth/me/",
            headers=AuthService.auth_headers(),
            timeout=10
        )

    @staticmethod
    def set_token(token):
        """Store JWT token"""
        AuthService.token = token

    @staticmethod
    def set_user(user_data):
        """Store user data"""
        AuthService.user = user_data

    @staticmethod
    def get_token():
        """Get stored token"""
        return AuthService.token

    @staticmethod
    def auth_headers():
        """Get authorization headers with token"""
        if AuthService.token:
            return {"Authorization": f"Bearer {AuthService.token}"}
        return {}

    @staticmethod
    def is_authenticated():
        """Check if user is authenticated"""
        return AuthService.token is not None

    @staticmethod
    def logout():
        """Logout and clear token"""
        AuthService.token = None
        AuthService.user = None
