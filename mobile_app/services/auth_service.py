import requests
from utils.config import BASE_URL


class AuthService:
    token = None

    @staticmethod
    def login(email, password):
        return requests.post(
            f"{BASE_URL}/login/",
            json={
                "email": email,
                "password": password
            },
            timeout=5
        )

    @staticmethod
    def register(name, email, password, role="donor"):
        return requests.post(
            f"{BASE_URL}/register/",
            json={
                "name": name,
                "email": email,
                "password": password,
                "role": role
            },
            timeout=5
        )

    @staticmethod
    def verify_otp(email, otp):
        return requests.post(
            f"{BASE_URL}/verify-otp/",
            json={
                "email": email,
                "otp": otp
            },
            timeout=5
        )

    @staticmethod
    def set_token(token):
        AuthService.token = token

    @staticmethod
    def get_token():
        return AuthService.token