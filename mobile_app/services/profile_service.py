import requests
from utils.config import BASE_URL
from services.auth_service import AuthService


class ProfileService:
    @staticmethod
    def get_donor_profile():
        """Get current donor profile"""
        return requests.get(
            f"{BASE_URL}/profiles/donor/me/",
            headers=AuthService.auth_headers(),
            timeout=10
        )

    @staticmethod
    def update_donor_profile(full_name=None, address=None):
        """Update donor profile"""
        data = {}
        if full_name:
            data["full_name"] = full_name
        if address:
            data["address"] = address
        
        return requests.patch(
            f"{BASE_URL}/profiles/donor/me/",
            json=data,
            headers=AuthService.auth_headers(),
            timeout=10
        )

    @staticmethod
    def get_ngo_profile():
        """Get current NGO profile"""
        return requests.get(
            f"{BASE_URL}/profiles/ngo/me/",
            headers=AuthService.auth_headers(),
            timeout=10
        )

    @staticmethod
    def update_ngo_profile(organization_name=None, registration_number=None, address=None):
        """Update NGO profile"""
        data = {}
        if organization_name:
            data["organization_name"] = organization_name
        if registration_number:
            data["registration_number"] = registration_number
        if address:
            data["address"] = address
        
        return requests.patch(
            f"{BASE_URL}/profiles/ngo/me/",
            json=data,
            headers=AuthService.auth_headers(),
            timeout=10
        )
