import requests
from utils.config import BASE_URL
from services.auth_service import AuthService


class DonationService:
    TIMEOUT = 10

    @staticmethod
    def _normalize_payload(**kwargs):
        data = {}
        for key, value in kwargs.items():
            if value is None:
                continue
            data[key] = str(value) if not isinstance(value, str) else value
        return data

    @staticmethod
    def create_donation(
        title,
        description,
        category,
        quantity,
        expiry_date=None,
        latitude=None,
        longitude=None,
        image=None,
    ):
        data = DonationService._normalize_payload(
            title=title,
            description=description,
            category=category,
            quantity=quantity,
            expiry_date=expiry_date,
            latitude=latitude,
            longitude=longitude,
        )

        if image:
            with open(image, "rb") as image_file:
                return requests.post(
                    f"{BASE_URL}/donations/",
                    data=data,
                    files={"image": image_file},
                    headers=AuthService.auth_headers(),
                    timeout=DonationService.TIMEOUT,
                )

        return requests.post(
            f"{BASE_URL}/donations/",
            json=data,
            headers=AuthService.auth_headers(),
            timeout=DonationService.TIMEOUT,
        )

    @staticmethod
    def get_donations(page=None, category=None, status=None, donor=None):
        params = {}

        if page is not None:
            params["page"] = page
        if category:
            params["category"] = category
        if status:
            params["status"] = status
        if donor:
            params["donor"] = donor

        return requests.get(
            f"{BASE_URL}/donations/",
            params=params,
            headers=AuthService.auth_headers(),
            timeout=DonationService.TIMEOUT,
        )

    @staticmethod
    def get_donation_detail(donation_id):
        return requests.get(
            f"{BASE_URL}/donations/{donation_id}/",
            headers=AuthService.auth_headers(),
            timeout=DonationService.TIMEOUT,
        )

    @staticmethod
    def update_donation(donation_id, **kwargs):
        image = kwargs.pop("image", None)
        data = DonationService._normalize_payload(**kwargs)

        if image:
            with open(image, "rb") as image_file:
                return requests.patch(
                    f"{BASE_URL}/donations/{donation_id}/",
                    data=data,
                    files={"image": image_file},
                    headers=AuthService.auth_headers(),
                    timeout=DonationService.TIMEOUT,
                )

        return requests.patch(
            f"{BASE_URL}/donations/{donation_id}/",
            json=data,
            headers=AuthService.auth_headers(),
            timeout=DonationService.TIMEOUT,
        )

    @staticmethod
    def delete_donation(donation_id):
        return requests.delete(
            f"{BASE_URL}/donations/{donation_id}/",
            headers=AuthService.auth_headers(),
            timeout=DonationService.TIMEOUT,
        )

    @staticmethod
    def get_donation_claims(donation_id):
        return requests.get(
            f"{BASE_URL}/donations/{donation_id}/claims/",
            headers=AuthService.auth_headers(),
            timeout=DonationService.TIMEOUT,
        )

    @staticmethod
    def claim_donation(donation_id, message=""):
        return requests.post(
            f"{BASE_URL}/donations/{donation_id}/claim/",
            json={"message": message},
            headers=AuthService.auth_headers(),
            timeout=DonationService.TIMEOUT,
        )

    @staticmethod
    def get_my_donations():
        return DonationService.get_donations(donor="me")