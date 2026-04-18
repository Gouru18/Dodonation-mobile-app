import requests
from utils.config import BASE_URL
from services.auth_service import AuthService


class PermitService:
    @staticmethod
    def upload_permit(permit_file_path):
        """Upload NGO permit file"""
        with open(permit_file_path, 'rb') as f:
            files = {'permit_file': f}
            return requests.post(
                f"{BASE_URL}/profiles/permits/upload/",
                files=files,
                headers=AuthService.auth_headers(),
                timeout=20
            )

    @staticmethod
    def get_my_permit():
        """Get current NGO's permit"""
        return requests.get(
            f"{BASE_URL}/profiles/permits/",
            headers=AuthService.auth_headers(),
            timeout=10
        )

    @staticmethod
    def get_pending_permits():
        """Get all pending permits (admin only)"""
        return requests.get(
            f"{BASE_URL}/profiles/permits/",
            headers=AuthService.auth_headers(),
            timeout=10
        )

    @staticmethod
    def approve_permit(permit_id):
        """Approve a permit (admin only)"""
        return requests.patch(
            f"{BASE_URL}/profiles/permits/{permit_id}/approval/",
            json={"status": "approved"},
            headers=AuthService.auth_headers(),
            timeout=10
        )

    @staticmethod
    def reject_permit(permit_id, rejection_reason=''):
        """Reject a permit (admin only)"""
        return requests.patch(
            f"{BASE_URL}/profiles/permits/{permit_id}/approval/",
            json={
                "status": "rejected",
                "rejection_reason": rejection_reason
            },
            headers=AuthService.auth_headers(),
            timeout=10
        )

    @staticmethod
    def get_permit_status():
        """Get current permit status"""
        response = PermitService.get_my_permit()
        if response.status_code == 200:
            permits = response.json()
            if permits:
                return permits[0].get('status', 'none')
        return 'none'
