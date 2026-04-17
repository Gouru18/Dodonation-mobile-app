import requests
from config import BASE_URL

TIMEOUT = 5  # seconds

def login_user(email, password):
    return requests.post(
        f"{BASE_URL}/login/",
        json={
            "email": email,
            "password": password
        },
        timeout=TIMEOUT
    )

def register_user(name, email, password, role):
    return requests.post(
        f"{BASE_URL}/register/",
        json={
            "name": name,
            "email": email,
            "password": password,
            "role": role
        },
        timeout=TIMEOUT
    )

def verify_otp(email, otp):
    return requests.post(
        f"{BASE_URL}/verify-otp/",
        json={
            "email": email,
            "otp": otp
        },
        timeout=TIMEOUT
    )