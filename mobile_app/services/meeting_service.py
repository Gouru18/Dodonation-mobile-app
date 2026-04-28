import requests
from utils.config import BASE_URL
from services.auth_service import AuthService


class MeetingService:
    @staticmethod
    def create_meeting(claim_id, scheduled_time, meeting_link):
        data = {
            "claim_request": claim_id,
            "scheduled_time": scheduled_time,
            "meeting_link": meeting_link,
        }

        return requests.post(
            f"{BASE_URL}/meetings/",
            json=data,
            headers=AuthService.auth_headers(),
            timeout=10
        )

    @staticmethod
    def get_my_meetings():
        return requests.get(
            f"{BASE_URL}/meetings/",
            headers=AuthService.auth_headers(),
            timeout=10
        )

    @staticmethod
    def get_meeting_detail(meeting_id):
        return requests.get(
            f"{BASE_URL}/meetings/{meeting_id}/",
            headers=AuthService.auth_headers(),
            timeout=10
        )

    @staticmethod
    def update_meeting(meeting_id, **kwargs):
        return requests.patch(
            f"{BASE_URL}/meetings/{meeting_id}/",
            json=kwargs,
            headers=AuthService.auth_headers(),
            timeout=10
        )

    @staticmethod
    def complete_online_meeting(meeting_id):
        return requests.post(
            f"{BASE_URL}/meetings/{meeting_id}/complete_online/",
            headers=AuthService.auth_headers(),
            timeout=10
        )

    @staticmethod
    def complete_physical_meeting(meeting_id):
        return requests.post(
            f"{BASE_URL}/meetings/{meeting_id}/complete_physical/",
            headers=AuthService.auth_headers(),
            timeout=10
        )

    @staticmethod
    def set_meeting_location(meeting_id, latitude, longitude, address=None):
        data = {
            "meeting_latitude": latitude,
            "meeting_longitude": longitude,
            "meeting_address": address,
        }

        return requests.post(
            f"{BASE_URL}/meetings/{meeting_id}/pin_location/",
            json=data,
            headers=AuthService.auth_headers(),
            timeout=10
        )

    @staticmethod
    def rate_donor(meeting_id, rating, comment=""):
        return requests.post(
            f"{BASE_URL}/donor-ratings/",
            json={
                "meeting": meeting_id,
                "rating": rating,
                "comment": comment,
            },
            headers=AuthService.auth_headers(),
            timeout=10
        )
