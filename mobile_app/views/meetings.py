import flet as ft

from services.auth_service import AuthService
from services.claim_service import ClaimService
from services.meeting_service import MeetingService
from utils.app_state import AppState
from utils.constants import PRIMARY_GREEN, SECONDARY_GREEN, BUTTON_TEXT, INPUT_TEXT
from utils.helpers import build_appbar, page_container, section_card, show_message


def meetings_view(page: ft.Page):
    is_donor = AuthService.user and AuthService.user.get("role") == "donor"
    meetings_column = ft.Column(spacing=12, scroll=ft.ScrollMode.AUTO, expand=True)
    accepted_claims_dropdown = ft.Dropdown(label="Accepted Claim", options=[])
    scheduled_time = ft.TextField(label="Scheduled Time (YYYY-MM-DD HH:MM:SS)", color=INPUT_TEXT)

    def load_accepted_claims():
        response = ClaimService.get_received_claims() if is_donor else ClaimService.get_sent_claims()
        accepted_claims_dropdown.options = []

        if response.status_code != 200:
            show_message(page, f"Could not load claims: {response.text}", "red")
            page.update()
            return

        for claim in response.json():
            if claim.get("status") == "accepted":
                donation = claim.get("donation") or {}
                accepted_claims_dropdown.options.append(
                    ft.dropdown.Option(str(claim["id"]), f"{donation.get('title', 'Donation')} ({claim['id']})")
                )
        page.update()

    def load_meetings():
        response = MeetingService.get_my_meetings()
        meetings_column.controls.clear()

        if response.status_code != 200:
            show_message(page, f"Could not load meetings: {response.text}", "red")
            page.update()
            return

        meetings = response.json()
        if not meetings:
            meetings_column.controls.append(ft.Text("No meetings scheduled yet."))
        else:
            for meeting in meetings:
                claim = meeting.get("claim_request") or {}
                donation = claim.get("donation") or {}
                notification = meeting.get("ngo_notification") or ""
                status_value = meeting.get("status", "")
                controls = [
                    ft.Text(donation.get("title", "Meeting"), size=18, weight=ft.FontWeight.BOLD),
                    ft.Text(f"When: {meeting.get('scheduled_time', '')}"),
                    ft.Text(f"Workflow: {status_value}"),
                    ft.Text(f"Google Meet: {meeting.get('meeting_link') or 'Not available'}"),
                ]

                if notification:
                    controls.append(ft.Text(notification, color="green"))

                if meeting.get("meeting_address"):
                    controls.append(ft.Text(f"Address: {meeting.get('meeting_address')}"))

                if is_donor and status_value == "online_scheduled":
                    controls.append(
                        ft.Button(
                            "Mark Online Meeting Complete",
                            on_click=lambda e, meeting_id=meeting["id"]: complete_online(meeting_id),
                            bgcolor=PRIMARY_GREEN,
                            color=BUTTON_TEXT,
                        )
                    )

                if is_donor and status_value == "online_completed":
                    controls.append(
                        ft.Button(
                            "Pin Physical Meeting Point",
                            on_click=lambda e, meeting_id=meeting["id"]: open_map(meeting_id),
                            bgcolor=SECONDARY_GREEN,
                            color=BUTTON_TEXT,
                        )
                    )

                if is_donor and status_value == "location_pinned":
                    controls.append(
                        ft.Button(
                            "Mark Physical Meeting Complete",
                            on_click=lambda e, meeting_id=meeting["id"]: complete_physical(meeting_id),
                            bgcolor=PRIMARY_GREEN,
                            color=BUTTON_TEXT,
                        )
                    )

                meetings_column.controls.append(
                    ft.Container(
                        content=ft.Column(controls, spacing=8),
                        padding=15,
                        border=ft.Border.all(1, "#d9d9d9"),
                        border_radius=12,
                        bgcolor="#FFFEFB",
                    )
                )
        page.update()

    def create_meeting(e):
        if not accepted_claims_dropdown.value or not scheduled_time.value:
            show_message(page, "Pick an accepted claim and scheduled time first.", "red")
            return

        response = MeetingService.create_meeting(
            claim_id=accepted_claims_dropdown.value,
            scheduled_time=scheduled_time.value,
        )

        if response.status_code in (200, 201):
            show_message(page, "Google Meet scheduled.", "green")
            scheduled_time.value = ""
            load_accepted_claims()
            load_meetings()
        else:
            show_message(page, f"Could not create meeting: {response.text}", "red")

    def complete_online(meeting_id):
        response = MeetingService.complete_online_meeting(meeting_id)
        if response.status_code == 200:
            show_message(page, "Online meeting marked complete.", "green")
            load_meetings()
        else:
            show_message(page, f"Could not complete online meeting: {response.text}", "red")

    def complete_physical(meeting_id):
        response = MeetingService.complete_physical_meeting(meeting_id)
        if response.status_code == 200:
            show_message(page, "Physical meeting completed.", "green")
            load_meetings()
        else:
            show_message(page, f"Could not complete physical meeting: {response.text}", "red")

    async def open_map(meeting_id):
        AppState.active_meeting_id = meeting_id
        await page.push_route("/map")

    async def go_back(e):
        await page.push_route("/dashboard")

    load_accepted_claims()
    load_meetings()

    return ft.View(
        route="/meetings",
        appbar=build_appbar("Meetings", go_back),
        controls=[
            page_container(
                section_card(
                    "Schedule Meeting",
                    [
                        accepted_claims_dropdown,
                        scheduled_time,
                        ft.Button("Schedule Google Meet", on_click=create_meeting, bgcolor=PRIMARY_GREEN, color=BUTTON_TEXT, width=220),
                    ],
                    subtitle="A donor can schedule an online Google Meet after accepting a claim.",
                ),
                section_card(
                    "My Meetings",
                    [
                        ft.Row(
                            [
                                ft.Text("Track the workflow from online call to physical handoff.", color="#4B5563"),
                                ft.Button("Refresh", on_click=lambda e: load_meetings(), bgcolor=SECONDARY_GREEN, color=BUTTON_TEXT),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        meetings_column,
                    ],
                ),
                ft.Row(
                    [ft.Button("Back", on_click=go_back, bgcolor="#666666", color=BUTTON_TEXT, width=140)],
                    alignment=ft.MainAxisAlignment.END,
                ),
            ),
        ],
    )
