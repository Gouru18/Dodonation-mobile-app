import flet as ft

from services.auth_service import AuthService
from services.claim_service import ClaimService
from services.meeting_service import MeetingService
from utils.app_state import AppState
from utils.constants import PRIMARY_GREEN, SECONDARY_GREEN, BUTTON_TEXT, INPUT_TEXT
from utils.helpers import show_message


def meetings_view(page: ft.Page):
    is_donor = AuthService.user and AuthService.user.get("role") == "donor"
    meetings_column = ft.Column(spacing=12, scroll=ft.ScrollMode.AUTO, expand=True)
    accepted_claims_dropdown = ft.Dropdown(label="Accepted Claim", options=[])
    scheduled_time = ft.TextField(label="Scheduled Time (YYYY-MM-DD HH:MM:SS)", color=INPUT_TEXT)
    meeting_link = ft.TextField(label="Meeting Link", color=INPUT_TEXT)
    meeting_address = ft.TextField(label="Meeting Address", color=INPUT_TEXT)

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
                meetings_column.controls.append(
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(donation.get("title", "Meeting"), size=18, weight=ft.FontWeight.BOLD),
                                ft.Text(f"When: {meeting.get('scheduled_time', '')}"),
                                ft.Text(f"Status: {meeting.get('status', '')}"),
                                ft.Text(f"Address: {meeting.get('meeting_address') or 'Not set'}"),
                                ft.Text(f"Link: {meeting.get('meeting_link') or 'None'}"),
                                ft.Row(
                                    [
                                        ft.Button(
                                            "Set Location",
                                            on_click=lambda e, meeting_id=meeting["id"]: open_map(meeting_id),
                                            bgcolor=SECONDARY_GREEN,
                                            color=BUTTON_TEXT,
                                        ),
                                        ft.Button(
                                            "Confirm",
                                            on_click=lambda e, meeting_id=meeting["id"]: confirm_meeting(meeting_id),
                                            bgcolor=PRIMARY_GREEN,
                                            color=BUTTON_TEXT,
                                        ),
                                    ],
                                    wrap=True,
                                ),
                            ],
                            spacing=8,
                        ),
                        padding=15,
                        border=ft.border.all(1, "#d9d9d9"),
                        border_radius=12,
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
            meeting_link=meeting_link.value or None,
            meeting_address=meeting_address.value or None,
        )

        if response.status_code in (200, 201):
            show_message(page, "Meeting created.", "green")
            scheduled_time.value = ""
            meeting_link.value = ""
            meeting_address.value = ""
            load_accepted_claims()
            load_meetings()
        else:
            show_message(page, f"Could not create meeting: {response.text}", "red")

    def confirm_meeting(meeting_id):
        response = MeetingService.confirm_meeting(meeting_id)
        if response.status_code == 200:
            show_message(page, "Meeting confirmed.", "green")
            load_meetings()
        else:
            show_message(page, f"Could not confirm meeting: {response.text}", "red")

    async def open_map(meeting_id):
        AppState.active_meeting_id = meeting_id
        await page.push_route("/map")

    async def go_back(e):
        await page.push_route("/dashboard")

    load_accepted_claims()
    load_meetings()

    return ft.View(
        route="/meetings",
        appbar=ft.AppBar(title=ft.Text("Meetings")),
        controls=[
            ft.Container(
                expand=True,
                padding=20,
                content=ft.Column(
                    [
                        ft.Text("Schedule Meeting", size=20, weight=ft.FontWeight.BOLD),
                        accepted_claims_dropdown,
                        scheduled_time,
                        meeting_link,
                        meeting_address,
                        ft.Button("Create Meeting", on_click=create_meeting, bgcolor=PRIMARY_GREEN, color=BUTTON_TEXT),
                        ft.Divider(),
                        ft.Row(
                            [
                                ft.Text("My Meetings", size=20, weight=ft.FontWeight.BOLD),
                                ft.Button("Refresh", on_click=lambda e: load_meetings(), bgcolor=SECONDARY_GREEN, color=BUTTON_TEXT),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        meetings_column,
                        ft.Button("Back", on_click=go_back, bgcolor="#666666", color=BUTTON_TEXT),
                    ],
                    spacing=15,
                    expand=True,
                ),
            )
        ],
    )
