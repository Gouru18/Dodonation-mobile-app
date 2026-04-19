import requests
from utils.config import BASE_URL
from services.auth_service import AuthService


class PermitService:
    TIMEOUT = 10

    @staticmethod
    def display_status(status):
        if not status:
            return "Unknown"

        normalized = str(status).strip().lower()
        mapping = {
            "approved": "Approved",
            "accepted": "Approved",
            "pending": "Pending",
            "rejected": "Rejected",
            "unknown": "Unknown",
            "none": "Not submitted",
        }
        return mapping.get(normalized, normalized.capitalize())

    @staticmethod
    def upload_permit(permit_file_path):
        with open(permit_file_path, "rb") as f:
            files = {"permit_file": f}
            return requests.post(
                f"{BASE_URL}/profiles/permits/upload/",
                files=files,
                headers=AuthService.auth_headers(),
                timeout=20,
            )

    @staticmethod
    def get_my_permit():
        return requests.get(
            f"{BASE_URL}/profiles/permits/",
            headers=AuthService.auth_headers(),
            timeout=PermitService.TIMEOUT,
        )

    @staticmethod
    def get_pending_permits():
        return requests.get(
            f"{BASE_URL}/profiles/permits/",
            headers=AuthService.auth_headers(),
            timeout=PermitService.TIMEOUT,
        )

    @staticmethod
    def approve_permit(permit_id):
        return requests.patch(
            f"{BASE_URL}/profiles/permits/{permit_id}/approval/",
            json={"status": "approved"},
            headers=AuthService.auth_headers(),
            timeout=PermitService.TIMEOUT,
        )

    @staticmethod
    def reject_permit(permit_id, rejection_reason=""):
        return requests.patch(
            f"{BASE_URL}/profiles/permits/{permit_id}/approval/",
            json={
                "status": "rejected",
                "rejection_reason": rejection_reason,
            },
            headers=AuthService.auth_headers(),
            timeout=PermitService.TIMEOUT,
        )

    @staticmethod
    def get_permit_status():
        response = PermitService.get_my_permit()
        if response.status_code == 200:
            permits = response.json()
            if permits:
                latest = permits[0]
                return PermitService.display_status(latest.get("status", "none"))
        return "Not submitted"