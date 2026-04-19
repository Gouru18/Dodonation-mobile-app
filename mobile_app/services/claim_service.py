import requests
from utils.config import BASE_URL
from services.auth_service import AuthService


class ClaimService:
    TIMEOUT = 10

    @staticmethod
    def get_my_claims():
        return requests.get(
            f"{BASE_URL}/claims/",
            headers=AuthService.auth_headers(),
            timeout=ClaimService.TIMEOUT,
        )

    @staticmethod
    def get_claim_detail(claim_id):
        return requests.get(
            f"{BASE_URL}/claims/{claim_id}/",
            headers=AuthService.auth_headers(),
            timeout=ClaimService.TIMEOUT,
        )

    @staticmethod
    def accept_claim(claim_id):
        return requests.post(
            f"{BASE_URL}/claims/{claim_id}/accept/",
            headers=AuthService.auth_headers(),
            timeout=ClaimService.TIMEOUT,
        )

    @staticmethod
    def reject_claim(claim_id):
        return requests.post(
            f"{BASE_URL}/claims/{claim_id}/reject/",
            headers=AuthService.auth_headers(),
            timeout=ClaimService.TIMEOUT,
        )

    @staticmethod
    def get_received_claims():
        return requests.get(
            f"{BASE_URL}/claims/",
            params={"type": "received"},
            headers=AuthService.auth_headers(),
            timeout=ClaimService.TIMEOUT,
        )

    @staticmethod
    def get_sent_claims():
        return requests.get(
            f"{BASE_URL}/claims/",
            params={"type": "sent"},
            headers=AuthService.auth_headers(),
            timeout=ClaimService.TIMEOUT,
        )

    @staticmethod
    def delete_claim(claim_id):
        return requests.delete(
            f"{BASE_URL}/claims/{claim_id}/",
            headers=AuthService.auth_headers(),
            timeout=ClaimService.TIMEOUT,
        )
