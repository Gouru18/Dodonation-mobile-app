import json
import os

MEET_SCOPE = "https://www.googleapis.com/auth/meetings.space.created"
MEET_CREATE_URL = "https://meet.googleapis.com/v2/spaces"


class GoogleMeetError(Exception):
    pass


def _get_google_credentials():
    from google.auth import default
    from google.auth.transport.requests import Request
    from google.oauth2 import service_account

    service_account_json = os.getenv("GOOGLE_MEET_SERVICE_ACCOUNT_JSON")
    if service_account_json:
        try:
            info = json.loads(service_account_json)
        except json.JSONDecodeError as exc:
            raise GoogleMeetError("GOOGLE_MEET_SERVICE_ACCOUNT_JSON is not valid JSON.") from exc

        credentials = service_account.Credentials.from_service_account_info(
            info,
            scopes=[MEET_SCOPE],
        )
    else:
        credentials, _ = default(scopes=[MEET_SCOPE])

    credentials.refresh(Request())
    return credentials


def create_google_meet_space():
    import requests

    credentials = _get_google_credentials()

    response = requests.post(
        MEET_CREATE_URL,
        headers={
            "Authorization": f"Bearer {credentials.token}",
            "Content-Type": "application/json",
        },
        json={},
        timeout=15,
    )

    if response.status_code >= 400:
        try:
            payload = response.json()
        except ValueError:
            payload = {"error": {"message": response.text}}
        message = payload.get("error", {}).get("message", "Failed to create Google Meet space.")
        raise GoogleMeetError(message)

    payload = response.json()
    return {
        "space_name": payload.get("name"),
        "meeting_uri": payload.get("meetingUri"),
    }
