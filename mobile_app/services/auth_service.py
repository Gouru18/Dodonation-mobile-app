import json
import requests
from utils.config import BASE_URL


class AuthService:
    TIMEOUT = 10
    token = None
    user = None
    _storage_fallback = {}

    STORAGE_TOKEN_KEY = "auth_token"
    STORAGE_USER_KEY = "auth_user"
    STORAGE_PENDING_OTP_EMAIL_KEY = "pending_otp_email"

    @staticmethod
    def register_donor(username, email, password, full_name, phone=""):
        return requests.post(
            f"{BASE_URL}/auth/register/donor/",
            json={
                "username": username,
                "email": email,
                "password": password,
                "full_name": full_name,
                "phone": phone,
            },
            timeout=AuthService.TIMEOUT,
        )

    @staticmethod
    def register_ngo(
        username,
        email,
        password,
        organization_name,
        permit_file_path,
        phone="",
        registration_number="",
    ):
        data = {
            "username": username,
            "email": email,
            "password": password,
            "organization_name": organization_name,
            "phone": phone,
            "registration_number": registration_number,
        }

        with open(permit_file_path, "rb") as permit_file:
            return requests.post(
                f"{BASE_URL}/auth/register/ngo/",
                data=data,
                files={"permit_file": permit_file},
                timeout=20,
            )

    @staticmethod
    def login(identifier, password):
        return requests.post(
            f"{BASE_URL}/auth/login/",
            json={
                "identifier": identifier,
                "password": password,
            },
            timeout=AuthService.TIMEOUT,
        )

    @staticmethod
    def verify_otp(email, otp):
        return requests.post(
            f"{BASE_URL}/auth/verify-otp/",
            json={
                "email": email,
                "otp": otp,
            },
            timeout=AuthService.TIMEOUT,
        )

    @staticmethod
    def request_otp(email):
        return requests.post(
            f"{BASE_URL}/auth/request-otp/",
            json={"email": email},
            timeout=AuthService.TIMEOUT,
        )

    @staticmethod
    def get_current_user():
        return requests.get(
            f"{BASE_URL}/auth/me/",
            headers=AuthService.auth_headers(),
            timeout=AuthService.TIMEOUT,
        )

    @staticmethod
    def set_token(token):
        AuthService.token = token

    @staticmethod
    def set_user(user_data):
        AuthService.user = user_data

    @staticmethod
    def get_token():
        return AuthService.token

    @staticmethod
    def get_user():
        return AuthService.user

    @staticmethod
    def auth_headers():
        if AuthService.token:
            return {"Authorization": f"Bearer {AuthService.token}"}
        return {}

    @staticmethod
    def is_authenticated():
        return bool(AuthService.token)

    @staticmethod
    def logout():
        AuthService.token = None
        AuthService.user = None

    @staticmethod
    def _get_client_storage(page):
        return getattr(page, "client_storage", None)

    @staticmethod
    async def persist_session(page: "ft.Page"):
        client_storage = AuthService._get_client_storage(page)
        if AuthService.token is not None:
            if client_storage:
                await client_storage.set_async(
                    AuthService.STORAGE_TOKEN_KEY,
                    AuthService.token,
                )
            else:
                AuthService._storage_fallback[AuthService.STORAGE_TOKEN_KEY] = AuthService.token
        else:
            if client_storage:
                await client_storage.remove_async(AuthService.STORAGE_TOKEN_KEY)
            else:
                AuthService._storage_fallback.pop(AuthService.STORAGE_TOKEN_KEY, None)

        if AuthService.user is not None:
            user_json = json.dumps(AuthService.user)
            if client_storage:
                await client_storage.set_async(
                    AuthService.STORAGE_USER_KEY,
                    user_json,
                )
            else:
                AuthService._storage_fallback[AuthService.STORAGE_USER_KEY] = user_json
        else:
            if client_storage:
                await client_storage.remove_async(AuthService.STORAGE_USER_KEY)
            else:
                AuthService._storage_fallback.pop(AuthService.STORAGE_USER_KEY, None)

    @staticmethod
    async def restore_session(page: "ft.Page"):
        client_storage = AuthService._get_client_storage(page)
        if client_storage:
            token = await client_storage.get_async(AuthService.STORAGE_TOKEN_KEY)
            user_raw = await client_storage.get_async(AuthService.STORAGE_USER_KEY)
        else:
            token = AuthService._storage_fallback.get(AuthService.STORAGE_TOKEN_KEY)
            user_raw = AuthService._storage_fallback.get(AuthService.STORAGE_USER_KEY)

        AuthService.token = token or None

        if user_raw:
            try:
                AuthService.user = json.loads(user_raw)
            except Exception:
                AuthService.user = None
        else:
            AuthService.user = None

    @staticmethod
    async def clear_session(page: "ft.Page"):
        AuthService.logout()
        client_storage = AuthService._get_client_storage(page)
        if client_storage:
            await client_storage.remove_async(AuthService.STORAGE_TOKEN_KEY)
            await client_storage.remove_async(AuthService.STORAGE_USER_KEY)
        else:
            AuthService._storage_fallback.pop(AuthService.STORAGE_TOKEN_KEY, None)
            AuthService._storage_fallback.pop(AuthService.STORAGE_USER_KEY, None)

    @staticmethod
    async def set_pending_otp_email(page: "ft.Page", email: str):
        client_storage = AuthService._get_client_storage(page)
        if client_storage:
            await client_storage.set_async(
                AuthService.STORAGE_PENDING_OTP_EMAIL_KEY,
                email or "",
            )
        else:
            AuthService._storage_fallback[AuthService.STORAGE_PENDING_OTP_EMAIL_KEY] = email or ""

    @staticmethod
    async def get_pending_otp_email(page: "ft.Page"):
        client_storage = AuthService._get_client_storage(page)
        if client_storage:
            return await client_storage.get_async(
                AuthService.STORAGE_PENDING_OTP_EMAIL_KEY
            )
        return AuthService._storage_fallback.get(
            AuthService.STORAGE_PENDING_OTP_EMAIL_KEY
        )

    @staticmethod
    async def clear_pending_otp_email(page: "ft.Page"):
        client_storage = AuthService._get_client_storage(page)
        if client_storage:
            await client_storage.remove_async(
                AuthService.STORAGE_PENDING_OTP_EMAIL_KEY
            )
        else:
            AuthService._storage_fallback.pop(
                AuthService.STORAGE_PENDING_OTP_EMAIL_KEY,
                None,
            )
