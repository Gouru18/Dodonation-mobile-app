import webbrowser
import flet as ft

from services.auth_service import AuthService
from services.claim_service import ClaimService
from services.meeting_service import MeetingService
from utils.app_state import AppState
from utils.constants import PRIMARY_GREEN, SECONDARY_GREEN, BUTTON_TEXT, INPUT_TEXT
from utils.helpers import (
    build_appbar,
    page_container,
    centered_content,
    section_card,
    auth_input,
    primary_button,
    secondary_button,
    muted_text,
    status_chip,
    show_error,
    show_success,
)


def meetings_view(page: ft.Page):
    user = AuthService.user or {}
    is_donor = user.get("role") == "donor"
    reschedule_state = {"meeting_id": None}
    schedule_meeting_button = None
    clear_schedule_button = None

    meetings_column = ft.Column(spacing=12, scroll=ft.ScrollMode.AUTO, expand=True)

    accepted_claims_dropdown = ft.Dropdown(
        label="Accepted Claim",
        options=[],
        border_radius=14,
        filled=True,
        bgcolor="white",
    )

    scheduled_time = auth_input(
        "Scheduled Time (YYYY-MM-DD HH:MM:SS)",
        ft.Icons.CALENDAR_MONTH,
    )

    meeting_link = auth_input(
        "Google Meet Link",
        ft.Icons.VIDEO_CALL,
    )
    meeting_link.hint_text = "Paste the Google Meet link"

    def refresh_schedule_controls():
        if schedule_meeting_button is not None:
            schedule_meeting_button.text = schedule_button_text()
        if clear_schedule_button is not None:
            clear_schedule_button.visible = bool(reschedule_state["meeting_id"])

    def clear_schedule_form():
        accepted_claims_dropdown.value = None
        scheduled_time.value = ""
        meeting_link.value = ""
        reschedule_state["meeting_id"] = None
        refresh_schedule_controls()
        page.update()

    def open_meeting_link(link):
        if not link or link == "Not available":
            show_error(page, "No online meeting link is available yet.")
            return

        try:
            opened = webbrowser.open(link)
            if not opened:
                page.launch_url(link)
        except Exception:
            try:
                page.launch_url(link)
            except Exception as ex:
                show_error(page, f"Could not open meeting link: {ex}")

    def workflow_color(status_value):
        return {
            "online_scheduled": "#1D4ED8",
            "online_completed": "#027A48",
            "location_pinned": "#B54708",
            "physical_completed": "#027A48",
            "expired": "#B42318",
            "cancelled": "#B42318",
        }.get(status_value, "#667085")

    def schedule_button_text():
        return "Reschedule Meeting" if reschedule_state["meeting_id"] else "Schedule Meeting"

    def begin_reschedule(meeting):
        claim = meeting.get("claim_request_data") or {}
        reschedule_state["meeting_id"] = meeting.get("id")
        accepted_claims_dropdown.value = str(claim.get("id", ""))
        scheduled_time.value = meeting.get("scheduled_time", "") or ""
        meeting_link.value = meeting.get("meeting_link", "") or ""
        refresh_schedule_controls()
        page.update()

    def load_accepted_claims():
        response = ClaimService.get_received_claims() if is_donor else ClaimService.get_sent_claims()
        accepted_claims_dropdown.options = []

        if response.status_code != 200:
            show_error(page, f"Could not load claims: {response.text}")
            page.update()
            return

        for claim in response.json():
            if claim.get("status") == "accepted":
                donation = claim.get("donation") or {}
                accepted_claims_dropdown.options.append(
                    ft.dropdown.Option(
                        str(claim["id"]),
                        f"{donation.get('title', 'Donation')} (Claim #{claim['id']})"
                    )
                )

        page.update()

    def meeting_card(meeting):
        claim = meeting.get("claim_request_data") or meeting.get("claim_request") or {}
        donation = claim.get("donation") or {}
        status_value = meeting.get("display_status") or meeting.get("status", "")
        notification = meeting.get("ngo_notification") or ""
        link_value = meeting.get("meeting_link") or "Not available"
        is_expired = bool(meeting.get("is_online_expired"))
        has_joinable_link = bool(meeting.get("meeting_link")) and not is_expired

        controls = [
            ft.Row(
                [
                    ft.Text(
                        donation.get("title", "Meeting"),
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        expand=True,
                    ),
                    status_chip(
                        status_value.replace("_", " ").title(),
                        color=workflow_color(status_value),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            muted_text(f"When: {meeting.get('scheduled_time', 'Not set')}"),
            muted_text(f"Google Meet: {link_value}"),
        ]

        if has_joinable_link and status_value in {"online_scheduled", "online_completed"}:
            controls.append(
                secondary_button(
                    "Join Online Meeting",
                    lambda e, current_link=meeting.get("meeting_link"): open_meeting_link(current_link),
                    width=220,
                    icon=ft.Icons.VIDEO_CALL,
                )
            )

        if meeting.get("meeting_address"):
            controls.append(muted_text(f"Address: {meeting.get('meeting_address')}"))

        if notification:
            controls.append(muted_text(notification))

        if is_donor:
            if status_value == "expired":
                controls.extend(
                    [
                        muted_text("This online meeting link has expired because the scheduled time has passed."),
                        primary_button(
                            "Reschedule Online Meeting",
                            lambda e, current_meeting=meeting: begin_reschedule(current_meeting),
                            width=250,
                            icon=ft.Icons.EDIT,
                        ),
                    ]
                )
            elif status_value == "online_scheduled":
                controls.append(
                    primary_button(
                        "Mark Online Meeting Complete",
                        lambda e, meeting_id=meeting["id"]: complete_online(meeting_id),
                        width=250,
                        icon=ft.Icons.CHECK_CIRCLE,
                    )
                )

            elif status_value == "online_completed":
                controls.append(
                    secondary_button(
                        "Pin Physical Meeting Point",
                        lambda e, meeting_id=meeting["id"]: page.run_task(open_map, meeting_id),
                        width=240,
                        icon=ft.Icons.MAP,
                    )
                )

            elif status_value == "location_pinned":
                controls.append(
                    primary_button(
                        "Mark Physical Meeting Complete",
                        lambda e, meeting_id=meeting["id"]: complete_physical(meeting_id),
                        width=260,
                        icon=ft.Icons.DONE_ALL,
                    )
                )

            elif status_value == "physical_completed":
                controls.append(
                    ft.Text("Donation handoff completed.", color="green")
                )

        else:
            if status_value == "expired":
                controls.append(ft.Text("This online meeting link has expired. Waiting for the donor to reschedule it."))
            elif status_value == "online_scheduled":
                controls.append(ft.Text("Join the online meeting using the Google Meet link above."))
            elif status_value == "online_completed":
                controls.append(
                    secondary_button(
                        "Pin Physical Meeting Point",
                        lambda e, meeting_id=meeting["id"]: page.run_task(open_map, meeting_id),
                        width=240,
                        icon=ft.Icons.MAP,
                    )
                )
            elif status_value == "location_pinned":
                controls.append(ft.Text("Meeting location is ready. Proceed to handoff.", color="blue"))
            elif status_value == "physical_completed":
                controls.append(ft.Text("Donation handoff completed.", color="green"))

        return ft.Container(
            content=ft.Column(controls, spacing=8),
            padding=15,
            border=ft.Border.all(1, "#d9d9d9"),
            border_radius=12,
            bgcolor="#FFFEFB",
        )

    def load_meetings():
        response = MeetingService.get_my_meetings()
        meetings_column.controls.clear()

        if response.status_code != 200:
            show_error(page, f"Could not load meetings: {response.text}")
            page.update()
            return

        meetings = response.json()

        if not meetings:
            meetings_column.controls.append(ft.Text("No meetings scheduled yet."))
        else:
            for meeting in meetings:
                meetings_column.controls.append(meeting_card(meeting))

        page.update()

    def create_meeting(e):
        if not is_donor:
            show_error(page, "Only donors can schedule meetings.")
            return

        if not accepted_claims_dropdown.value or not scheduled_time.value or not meeting_link.value:
            show_error(page, "Pick an accepted claim, scheduled time, and Google Meet link first.")
            return

        if "meet.google.com" not in meeting_link.value.lower():
            show_error(page, "Please paste a valid Google Meet link.")
            return

        if reschedule_state["meeting_id"]:
            response = MeetingService.update_meeting(
                reschedule_state["meeting_id"],
                scheduled_time=scheduled_time.value,
                meeting_link=meeting_link.value,
                status="online_scheduled",
            )
        else:
            response = MeetingService.create_meeting(
                claim_id=accepted_claims_dropdown.value,
                scheduled_time=scheduled_time.value,
                meeting_link=meeting_link.value,
            )

        if response.status_code in (200, 201):
            show_success(
                page,
                "Meeting rescheduled successfully."
                if reschedule_state["meeting_id"]
                else "Meeting scheduled successfully.",
            )
            clear_schedule_form()
            load_accepted_claims()
            load_meetings()
        else:
            show_error(page, f"Could not create meeting: {response.text}")

    def complete_online(meeting_id):
        response = MeetingService.complete_online_meeting(meeting_id)
        if response.status_code == 200:
            show_success(page, "Online meeting marked complete.")
            load_meetings()
        else:
            show_error(page, f"Could not complete online meeting: {response.text}")

    def complete_physical(meeting_id):
        response = MeetingService.complete_physical_meeting(meeting_id)
        if response.status_code == 200:
            show_success(page, "Physical meeting completed.")
            load_meetings()
        else:
            show_error(page, f"Could not complete physical meeting: {response.text}")

    async def open_map(meeting_id):
        AppState.active_meeting_id = meeting_id
        await page.push_route("/map")

    async def go_back(e):
        await page.push_route("/dashboard")

    schedule_meeting_button = primary_button(
        "Schedule Meeting",
        create_meeting,
        width=220,
        icon=ft.Icons.VIDEO_CALL,
    )
    clear_schedule_button = secondary_button(
        "Clear",
        lambda e: clear_schedule_form(),
        width=160,
        icon=ft.Icons.CLOSE,
    )
    clear_schedule_button.visible = False

    if is_donor:
        load_accepted_claims()
    load_meetings()

    page_sections = []
    if is_donor:
        page_sections.append(
            section_card(
                "Schedule Meeting",
                [
                    muted_text(
                        "Donors can schedule the online Google Meet after accepting a claim."
                    ),
                    accepted_claims_dropdown,
                    scheduled_time,
                    meeting_link,
                    ft.Row(
                        [
                            schedule_meeting_button,
                            clear_schedule_button,
                        ],
                        wrap=True,
                        spacing=12,
                    ),
                ],
                subtitle="Online meeting first, then physical handoff.",
            )
        )

    page_sections.extend(
        [
            section_card(
                "My Meetings",
                [
                    ft.Row(
                        [
                            ft.Text(
                                "Track the workflow from online meeting to physical handoff.",
                                color="#4B5563",
                            ),
                            secondary_button(
                                "Refresh",
                                lambda e: load_meetings(),
                                width=140,
                                icon=ft.Icons.REFRESH,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        wrap=True,
                    ),
                    meetings_column,
                ],
            ),
            ft.Row(
                [
                    secondary_button(
                        "Back",
                        go_back,
                        width=140,
                        icon=ft.Icons.ARROW_BACK,
                    )
                ],
                alignment=ft.MainAxisAlignment.END,
            ),
        ]
    )

    return ft.View(
        route="/meetings",
        appbar=build_appbar("Meetings", go_back),
        controls=[
            page_container(
                centered_content(
                    *page_sections,
                ),
            ),
        ],
    )
