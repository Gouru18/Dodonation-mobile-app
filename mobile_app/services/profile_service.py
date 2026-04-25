import requests
from utils.config import BASE_URL
from services.auth_service import AuthService


class ProfileService:
    TIMEOUT = 10

    @staticmethod
    def get_donor_profile():
        return requests.get(
            f"{BASE_URL}/profiles/donor/me/",
            headers=AuthService.auth_headers(),
            timeout=ProfileService.TIMEOUT,
        )

    @staticmethod
    def update_donor_profile(full_name=None, address=None, phone=None):
        data = {}

        if full_name is not None:
            data["full_name"] = full_name

        if address is not None:
            data["address"] = address

        if phone is not None:
            data["phone"] = phone

        return requests.patch(
            f"{BASE_URL}/profiles/donor/me/",
            json=data,
            headers=AuthService.auth_headers(),
            timeout=ProfileService.TIMEOUT,
        )

    @staticmethod
    def get_ngo_profile():
        return requests.get(
            f"{BASE_URL}/profiles/ngo/me/",
            headers=AuthService.auth_headers(),
            timeout=ProfileService.TIMEOUT,
        )

    @staticmethod
    def update_ngo_profile(
        organization_name=None,
        registration_number=None,
        address=None,
        phone=None,
    ):
        data = {}

        if organization_name is not None:
            data["organization_name"] = organization_name

        if registration_number is not None:
            data["registration_number"] = registration_number

        if address is not None:
            data["address"] = address

        if phone is not None:
            data["phone"] = phone

        return requests.patch(
            f"{BASE_URL}/profiles/ngo/me/",
            json=data,
            headers=AuthService.auth_headers(),
            timeout=ProfileService.TIMEOUT,
        )
