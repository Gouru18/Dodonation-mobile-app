import requests
from utils.config import BASE_URL
from services.auth_service import AuthService


class DonationService:
    @staticmethod
    def create_donation(title, description, category, quantity, expiry_date=None, latitude=None, longitude=None, image=None):
        """Create a new donation"""
        data = {
            "title": title,
            "description": description,
            "category": category,
            "quantity": quantity,
            "expiry_date": expiry_date,
            "latitude": latitude,
            "longitude": longitude,
        }

        if image:
            with open(image, 'rb') as image_file:
                return requests.post(
                    f"{BASE_URL}/donations/",
                    data=data,
                    files={"image": image_file},
                    headers=AuthService.auth_headers(),
                    timeout=10
                )

        return requests.post(
            f"{BASE_URL}/donations/",
            json=data,
            headers=AuthService.auth_headers(),
            timeout=10
        )

    @staticmethod
    def get_donations(page=1, category=None, status=None):
        """Get list of donations with optional filters"""
        params = {"page": page}
        if category:
            params["category"] = category
        if status:
            params["status"] = status
        
        return requests.get(
            f"{BASE_URL}/donations/",
            params=params,
            headers=AuthService.auth_headers(),
            timeout=10
        )

    @staticmethod
    def get_donation_detail(donation_id):
        """Get donation details"""
        return requests.get(
            f"{BASE_URL}/donations/{donation_id}/",
            headers=AuthService.auth_headers(),
            timeout=10
        )

    @staticmethod
    def update_donation(donation_id, **kwargs):
        """Update donation"""
        return requests.patch(
            f"{BASE_URL}/donations/{donation_id}/",
            json=kwargs,
            headers=AuthService.auth_headers(),
            timeout=10
        )

    @staticmethod
    def get_donation_claims(donation_id):
        """Get all claims for a donation"""
        return requests.get(
            f"{BASE_URL}/donations/{donation_id}/claims/",
            headers=AuthService.auth_headers(),
            timeout=10
        )

    @staticmethod
    def claim_donation(donation_id, message=''):
        """NGO claims a donation"""
        return requests.post(
            f"{BASE_URL}/donations/{donation_id}/claim/",
            json={"message": message},
            headers=AuthService.auth_headers(),
            timeout=10
        )

    @staticmethod
    def get_my_donations():
        """Get current user's donations"""
        return requests.get(
            f"{BASE_URL}/donations/?donor=me",
            headers=AuthService.auth_headers(),
            timeout=10
        )
