import requests
from utils.config import BASE_URL
from services.auth_service import AuthService


class MeetingService:
    @staticmethod
    def create_meeting(claim_id, scheduled_time, meeting_link=None, 
                       meeting_latitude=None, meeting_longitude=None, meeting_address=None):
        """Create a meeting for an accepted claim"""
        data = {
            "claim_request": claim_id,
            "scheduled_time": scheduled_time,
            "meeting_link": meeting_link,
            "meeting_latitude": meeting_latitude,
            "meeting_longitude": meeting_longitude,
            "meeting_address": meeting_address,
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
        """Update meeting details"""
        return requests.patch(
            f"{BASE_URL}/meetings/{meeting_id}/",
            json=kwargs,
            headers=AuthService.auth_headers(),
            timeout=10
        )

    @staticmethod
    def confirm_meeting(meeting_id):
        """Confirm meeting"""
        return requests.post(
            f"{BASE_URL}/meetings/{meeting_id}/confirm/",
            headers=AuthService.auth_headers(),
            timeout=10
        )

    @staticmethod
    def complete_meeting(meeting_id):
        """Mark meeting as completed"""
        return requests.post(
            f"{BASE_URL}/meetings/{meeting_id}/complete/",
            headers=AuthService.auth_headers(),
            timeout=10
        )

    @staticmethod
    def set_meeting_location(meeting_id, latitude, longitude, address=None):
        """Set meeting location"""
        data = {
            "meeting_latitude": latitude,
            "meeting_longitude": longitude,
            "meeting_address": address,
        }
        
        return requests.patch(
            f"{BASE_URL}/meetings/{meeting_id}/",
            json=data,
            headers=AuthService.auth_headers(),
            timeout=10
        )
