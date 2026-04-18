import requests
from utils.config import BASE_URL
from services.auth_service import AuthService


class ClaimService:
    @staticmethod
    def get_my_claims():
        """Get claims sent/received by current user"""
        return requests.get(
            f"{BASE_URL}/claims/",
            headers=AuthService.auth_headers(),
            timeout=10
        )

    @staticmethod
    def get_claim_detail(claim_id):
        """Get claim details"""
        return requests.get(
            f"{BASE_URL}/claims/{claim_id}/",
            headers=AuthService.auth_headers(),
            timeout=10
        )

    @staticmethod
    def accept_claim(claim_id):
        """Donor accepts a claim request"""
        return requests.post(
            f"{BASE_URL}/claims/{claim_id}/accept/",
            headers=AuthService.auth_headers(),
            timeout=10
        )

    @staticmethod
    def reject_claim(claim_id):
        """Donor rejects a claim request"""
        return requests.post(
            f"{BASE_URL}/claims/{claim_id}/reject/",
            headers=AuthService.auth_headers(),
            timeout=10
        )

    @staticmethod
    def get_received_claims():
        """Get claims received by current user (for donors)"""
        return requests.get(
            f"{BASE_URL}/claims/?type=received",
            headers=AuthService.auth_headers(),
            timeout=10
        )

    @staticmethod
    def get_sent_claims():
        """Get claims sent by current user (for NGOs)"""
        return requests.get(
            f"{BASE_URL}/claims/?type=sent",
            headers=AuthService.auth_headers(),
            timeout=10
        )
