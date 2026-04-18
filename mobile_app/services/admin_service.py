import requests

from services.auth_service import AuthService
from utils.config import BASE_URL


class AdminService:
    @staticmethod
    def _request(method, path, json=None, params=None, files=None, data=None):
        return requests.request(
            method,
            f"{BASE_URL}/admin/{path}",
            json=json,
            params=params,
            files=files,
            data=data,
            headers=AuthService.auth_headers(),
            timeout=20,
        )

    @staticmethod
    def get_dashboard():
        return AdminService._request("GET", "dashboard/")

    @staticmethod
    def list_users(q=""):
        return AdminService._request("GET", "users/", params={"q": q} if q else None)

    @staticmethod
    def save_user(user_id=None, payload=None):
        if user_id:
            return AdminService._request("PATCH", f"users/{user_id}/", json=payload)
        return AdminService._request("POST", "users/", json=payload)

    @staticmethod
    def delete_user(user_id):
        return AdminService._request("DELETE", f"users/{user_id}/")

    @staticmethod
    def activate_user(user_id):
        return AdminService._request("POST", f"users/{user_id}/activate/")

    @staticmethod
    def suspend_user(user_id):
        return AdminService._request("POST", f"users/{user_id}/suspend/")

    @staticmethod
    def list_permits(q="", status=""):
        params = {}
        if q:
            params["q"] = q
        if status:
            params["status"] = status
        return AdminService._request("GET", "permits/", params=params or None)

    @staticmethod
    def delete_permit(permit_id):
        return AdminService._request("DELETE", f"permits/{permit_id}/")

    @staticmethod
    def approve_permit(permit_id):
        return AdminService._request("POST", f"permits/{permit_id}/approve/")

    @staticmethod
    def reject_permit(permit_id, rejection_reason=""):
        return AdminService._request("POST", f"permits/{permit_id}/reject/", json={"rejection_reason": rejection_reason})

    @staticmethod
    def save_permit(permit_id=None, ngo_id=None, permit_file_path=None, rejection_reason=""):
        data = {}
        if ngo_id:
            data["ngo_id"] = str(ngo_id)
        if rejection_reason:
            data["rejection_reason"] = rejection_reason

        files = None
        file_handle = None
        if permit_file_path:
            file_handle = open(permit_file_path, "rb")
            files = {"permit_file": file_handle}

        try:
            if permit_id:
                return AdminService._request("PATCH", f"permits/{permit_id}/", data=data or None, files=files)
            return AdminService._request("POST", "permits/", data=data or None, files=files)
        finally:
            if file_handle:
                file_handle.close()

    @staticmethod
    def list_donations(q=""):
        return AdminService._request("GET", "donations/", params={"q": q} if q else None)

    @staticmethod
    def save_donation(donation_id=None, payload=None):
        if donation_id:
            return AdminService._request("PATCH", f"donations/{donation_id}/", json=payload)
        return AdminService._request("POST", "donations/", json=payload)

    @staticmethod
    def save_donation_with_image(donation_id=None, payload=None, image_path=None):
        data = {}
        for key, value in (payload or {}).items():
            if value is None:
                continue
            data[key] = str(value)

        files = None
        file_handle = None
        if image_path:
            file_handle = open(image_path, "rb")
            files = {"image": file_handle}

        try:
            if donation_id:
                return AdminService._request("PATCH", f"donations/{donation_id}/", data=data or None, files=files)
            return AdminService._request("POST", "donations/", data=data or None, files=files)
        finally:
            if file_handle:
                file_handle.close()

    @staticmethod
    def delete_donation(donation_id):
        return AdminService._request("DELETE", f"donations/{donation_id}/")

    @staticmethod
    def list_claims(q=""):
        return AdminService._request("GET", "claims/", params={"q": q} if q else None)

    @staticmethod
    def save_claim(claim_id=None, payload=None):
        if claim_id:
            return AdminService._request("PATCH", f"claims/{claim_id}/", json=payload)
        return AdminService._request("POST", "claims/", json=payload)

    @staticmethod
    def delete_claim(claim_id):
        return AdminService._request("DELETE", f"claims/{claim_id}/")

    @staticmethod
    def list_meetings(q=""):
        return AdminService._request("GET", "meetings/", params={"q": q} if q else None)

    @staticmethod
    def save_meeting(meeting_id=None, payload=None):
        if meeting_id:
            return AdminService._request("PATCH", f"meetings/{meeting_id}/", json=payload)
        return AdminService._request("POST", "meetings/", json=payload)

    @staticmethod
    def delete_meeting(meeting_id):
        return AdminService._request("DELETE", f"meetings/{meeting_id}/")

    @staticmethod
    def list_faqs(q=""):
        return AdminService._request("GET", "faqs/", params={"q": q} if q else None)

    @staticmethod
    def save_faq(faq_id=None, payload=None):
        if faq_id:
            return AdminService._request("PATCH", f"faqs/{faq_id}/", json=payload)
        return AdminService._request("POST", "faqs/", json=payload)

    @staticmethod
    def delete_faq(faq_id):
        return AdminService._request("DELETE", f"faqs/{faq_id}/")

    @staticmethod
    def list_otp_codes(q=""):
        return AdminService._request("GET", "otp-codes/", params={"q": q} if q else None)

    @staticmethod
    def save_otp_code(otp_id=None, payload=None):
        if otp_id:
            return AdminService._request("PATCH", f"otp-codes/{otp_id}/", json=payload)
        return AdminService._request("POST", "otp-codes/", json=payload)

    @staticmethod
    def delete_otp_code(otp_id):
        return AdminService._request("DELETE", f"otp-codes/{otp_id}/")

    @staticmethod
    def list_donor_profiles(q=""):
        return AdminService._request("GET", "donor-profiles/", params={"q": q} if q else None)

    @staticmethod
    def save_donor_profile(profile_id=None, payload=None):
        if profile_id:
            return AdminService._request("PATCH", f"donor-profiles/{profile_id}/", json=payload)
        return AdminService._request("POST", "donor-profiles/", json=payload)

    @staticmethod
    def delete_donor_profile(profile_id):
        return AdminService._request("DELETE", f"donor-profiles/{profile_id}/")

    @staticmethod
    def list_ngo_profiles(q=""):
        return AdminService._request("GET", "ngo-profiles/", params={"q": q} if q else None)

    @staticmethod
    def save_ngo_profile(profile_id=None, payload=None):
        if profile_id:
            return AdminService._request("PATCH", f"ngo-profiles/{profile_id}/", json=payload)
        return AdminService._request("POST", "ngo-profiles/", json=payload)

    @staticmethod
    def delete_ngo_profile(profile_id):
        return AdminService._request("DELETE", f"ngo-profiles/{profile_id}/")
