import requests
from utils.config import BASE_URL
from services.auth_service import AuthService


class MeetingService:
    @staticmethod
    def create_meeting(claim_id, scheduled_time):
        """Create a Google Meet meeting for an accepted claim."""
        data = {
            "claim_request": claim_id,
            "scheduled_time": scheduled_time,
        }
        
        return requests.post(
            f"{BASE_URL}/meetings/",
            json=data,
            headers=AuthService.auth_headers(),
            timeout=10
        )

    @staticmethod
    def get_my_meetings():
        """Get all meetings for current user"""
        return requests.get(
            f"{BASE_URL}/meetings/",
            headers=AuthService.auth_headers(),
            timeout=10
        )

    @staticmethod
    def get_meeting_detail(meeting_id):
        """Get meeting details"""
        return requests.get(
            f"{BASE_URL}/meetings/{meeting_id}/",
            headers=AuthService.auth_headers(),
            timeout=10
        )

    @staticmethod
    def update_meeting(meeting_id, **kwargs):
        """Update meeting details before the online meeting is completed."""
        return requests.patch(
            f"{BASE_URL}/meetings/{meeting_id}/",
            json=kwargs,
            headers=AuthService.auth_headers(),
            timeout=10
        )

    @staticmethod
    def complete_online_meeting(meeting_id):
        """Mark the online Google Meet as completed."""
        return requests.post(
            f"{BASE_URL}/meetings/{meeting_id}/complete_online/",
            headers=AuthService.auth_headers(),
            timeout=10
        )

    @staticmethod
    def complete_physical_meeting(meeting_id):
        """Mark the physical handoff as completed."""
        return requests.post(
            f"{BASE_URL}/meetings/{meeting_id}/complete_physical/",
            headers=AuthService.auth_headers(),
            timeout=10
        )

    @staticmethod
    def set_meeting_location(meeting_id, latitude, longitude, address=None):
        """Pin the physical meeting location after the online meeting."""
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
