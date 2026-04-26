import webbrowser
from datetime import datetime, date, time
import flet as ft

from services.auth_service import AuthService
from services.claim_service import ClaimService
from services.meeting_service import MeetingService
from utils.app_state import AppState
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


def _inline_error():
    return ft.Text("", color="#B42318", size=12, visible=False)


def _field_block(field, error_label):
    return ft.Column([field, error_label], spacing=4)


def _set_inline_error(field, error_label, message):
    field.error_text = message
    error_label.value = message or ""
    error_label.visible = bool(message)


def _validate_meeting_date(value):
    raw = (value or "").strip()
    if not raw:
        return "Meeting date is required."
    try:
        parsed_date = datetime.strptime(raw, "%Y-%m-%d").date()
    except ValueError:
        return "Use a valid date in YYYY-MM-DD format."
    if parsed_date < date.today():
        return "Meeting date cannot be in the past."
    return None


def _validate_meeting_time(value, meeting_date_value=None):
    raw = (value or "").strip()
    if not raw:
        return "Meeting time is required."
    try:
        parsed_time = datetime.strptime(raw, "%H:%M").time()
    except ValueError:
        return "Use a valid time in HH:MM format."
    date_raw = (meeting_date_value or "").strip()
    if date_raw:
        try:
            parsed_date = datetime.strptime(date_raw, "%Y-%m-%d").date()
        except ValueError:
            return None
        if parsed_date == date.today():
            now_value = datetime.now().replace(second=0, microsecond=0)
            if datetime.combine(parsed_date, parsed_time) < now_value:
                return "Meeting time cannot be in the past for today."
    return None


def _format_scheduled_time(date_value, time_value):
    date_raw = (date_value or "").strip()
    time_raw = (time_value or "").strip()
    if not date_raw or not time_raw:
        return ""
    return f"{date_raw}T{time_raw}:00"


def _parse_picker_time(value):
    if isinstance(value, time):
        return value.replace(second=0, microsecond=0)

    raw = str(value or "").strip()
    if not raw:
        return None

    for fmt in ("%H:%M:%S", "%H:%M"):
        try:
            return datetime.strptime(raw, fmt).time().replace(second=0, microsecond=0)
        except ValueError:
            continue

    return None


def _format_picker_time(value):
    parsed_time = _parse_picker_time(value)
    if not parsed_time:
        return ""
    return parsed_time.strftime("%H:%M")


def _parse_picker_date(value):
    if isinstance(value, datetime):
        return value

    raw = str(value or "").strip()
    if not raw:
        return None

    try:
        return datetime.strptime(raw, "%Y-%m-%d")
    except ValueError:
        return None


def _format_picker_date(value):
    parsed_date = _parse_picker_date(value)
    if not parsed_date:
        return ""
    return parsed_date.strftime("%Y-%m-%d")


def _split_scheduled_time(value):
    raw = (value or "").strip()
    if not raw:
        return "", ""

    normalized = raw.replace("T", " ")
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"

    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S.%f"):
        try:
            parsed = datetime.strptime(normalized, fmt)
            return parsed.strftime("%Y-%m-%d"), parsed.strftime("%H:%M")
        except ValueError:
            continue

    try:
        parsed = datetime.fromisoformat(normalized)
        return parsed.strftime("%Y-%m-%d"), parsed.strftime("%H:%M")
    except ValueError:
        return raw[:10], raw[11:16] if len(raw) >= 16 else ""

    return None


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

    meeting_date = auth_input(
        "Meeting Date",
        ft.Icons.CALENDAR_MONTH,
    )
    meeting_date.read_only = True
    meeting_date.hint_text = "Pick a meeting date"
    meeting_date_error = _inline_error()
    meeting_time = auth_input(
        "Meeting Time",
        ft.Icons.ACCESS_TIME,
    )
    meeting_time.read_only = True
    meeting_time.hint_text = "Pick a meeting time"
    meeting_time_error = _inline_error()

    meeting_link = auth_input(
        "Google Meet Link",
        ft.Icons.VIDEO_CALL,
    )
    meeting_link.hint_text = "Paste the Google Meet link"

    def close_dialog():
        page.pop_dialog()

    def set_meeting_time_value(selected_time, update_page=True):
        meeting_time.value = _format_picker_time(selected_time)
        refresh_schedule_validation(update_page=update_page)

    def set_meeting_date_value(selected_date, update_page=True):
        meeting_date.value = _format_picker_date(selected_date)
        refresh_schedule_validation(update_page=update_page)

    def handle_time_picker_change(e):
        set_meeting_time_value(e.control.value)

    def handle_date_picker_change(e):
        set_meeting_date_value(e.control.value)

    date_picker = ft.DatePicker(
        modal=True,
        value=datetime.now(),
        first_date=datetime.combine(date.today(), time.min),
        last_date=datetime(date.today().year + 5, 12, 31),
        help_text="Select meeting date",
        confirm_text="Choose",
        cancel_text="Cancel",
        error_format_text="Pick a valid date.",
        error_invalid_text="Meeting date cannot be in the past.",
        entry_mode=ft.DatePickerEntryMode.CALENDAR_ONLY,
        on_change=handle_date_picker_change,
    )

    time_picker = ft.TimePicker(
        modal=True,
        value=datetime.now().time().replace(second=0, microsecond=0),
        help_text="Select meeting time",
        confirm_text="Choose",
        cancel_text="Cancel",
        error_invalid_text="Pick a valid meeting time.",
        entry_mode=ft.TimePickerEntryMode.DIAL_ONLY,
        hour_format=ft.TimePickerHourFormat.H24,
        on_change=handle_time_picker_change,
    )

    def open_time_picker(e):
        selected_time = _parse_picker_time(meeting_time.value)
        if selected_time:
            time_picker.value = selected_time
        else:
            time_picker.value = datetime.now().time().replace(second=0, microsecond=0)
        page.show_dialog(time_picker)

    def open_date_picker(e):
        selected_date = _parse_picker_date(meeting_date.value)
        date_picker.value = selected_date or datetime.combine(date.today(), time.min)
        page.show_dialog(date_picker)

    def open_dialog(title, content_controls, actions, modal=True):
        dialog = ft.AlertDialog(
            modal=modal,
            title=ft.Text(title, weight=ft.FontWeight.BOLD),
            content=ft.Column(content_controls, tight=True, spacing=10),
            actions=actions,
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dialog)

    def refresh_schedule_validation(*_, update_page=True):
        meeting_date_message = _validate_meeting_date(meeting_date.value)
        meeting_time_message = _validate_meeting_time(meeting_time.value, meeting_date.value)
        _set_inline_error(meeting_date, meeting_date_error, meeting_date_message)
        _set_inline_error(meeting_time, meeting_time_error, meeting_time_message)
        if update_page:
            page.update()

    def refresh_schedule_controls():
        if schedule_meeting_button is not None:
            schedule_meeting_button.text = schedule_button_text()
        if clear_schedule_button is not None:
            clear_schedule_button.visible = bool(reschedule_state["meeting_id"])

    def show_schedule_dialog():
        action_label = "reschedule" if reschedule_state["meeting_id"] else "schedule"
        open_dialog(
            "Confirm Meeting",
            [
                muted_text(
                    f"Are you sure you want to {action_label} this meeting for {meeting_date.value.strip()} at {meeting_time.value.strip()}?"
                ),
                muted_text(f"Google Meet link: {meeting_link.value.strip()}"),
            ],
            [
                ft.TextButton("Cancel", on_click=lambda e: close_dialog()),
                ft.TextButton("Confirm", on_click=lambda e: submit_meeting_schedule()),
            ],
        )

    def clear_schedule_form():
        accepted_claims_dropdown.value = None
        set_meeting_date_value("", update_page=False)
        set_meeting_time_value("", update_page=False)
        meeting_link.value = ""
        reschedule_state["meeting_id"] = None
        refresh_schedule_controls()
        refresh_schedule_validation()

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
            "location_pinned": "#D65606",
            "physical_completed": "#027A48",
            "expired": "#B42318",
            "cancelled": "#B42318",
        }.get(status_value, "#B9C2D5")

    def schedule_button_text():
        return "Reschedule Meeting" if reschedule_state["meeting_id"] else "Schedule Meeting"

    def begin_reschedule(meeting):
        claim = meeting.get("claim_request_data") or {}
        reschedule_state["meeting_id"] = meeting.get("id")
        accepted_claims_dropdown.value = str(claim.get("id", ""))
        existing_date, existing_time = _split_scheduled_time(meeting.get("scheduled_time", "") or "")
        set_meeting_date_value(existing_date, update_page=False)
        set_meeting_time_value(existing_time, update_page=False)
        meeting_link.value = meeting.get("meeting_link", "") or ""
        refresh_schedule_controls()
        refresh_schedule_validation()

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

    def validate_schedule_form():
        meeting_date_message = _validate_meeting_date(meeting_date.value)
        meeting_time_message = _validate_meeting_time(meeting_time.value, meeting_date.value)
        _set_inline_error(meeting_date, meeting_date_error, meeting_date_message)
        _set_inline_error(meeting_time, meeting_time_error, meeting_time_message)
        page.update()

        if not accepted_claims_dropdown.value or not meeting_date.value or not meeting_time.value or not meeting_link.value:
            show_error(page, "Pick an accepted claim, meeting date, meeting time, and Google Meet link first.")
            return False

        if meeting_date_message or meeting_time_message:
            show_error(page, "Please fix the highlighted meeting date and time fields.")
            return False

        if "meet.google.com" not in meeting_link.value.lower():
            show_error(page, "Please paste a valid Google Meet link.")
            return False

        return True

    def submit_meeting_schedule():
        close_dialog()

        scheduled_time = _format_scheduled_time(meeting_date.value, meeting_time.value)

        if reschedule_state["meeting_id"]:
            response = MeetingService.update_meeting(
                reschedule_state["meeting_id"],
                scheduled_time=scheduled_time,
                meeting_link=meeting_link.value,
                status="online_scheduled",
            )
        else:
            response = MeetingService.create_meeting(
                claim_id=accepted_claims_dropdown.value,
                scheduled_time=scheduled_time,
                meeting_link=meeting_link.value,
            )

        if response.status_code in (200, 201):
            meeting_payload = response.json()
            saved_meeting = MeetingService.get_meeting_detail(meeting_payload.get("id"))
            if saved_meeting.status_code != 200:
                show_error(page, "Meeting was submitted, but verification failed when reloading it.")
                return

            saved_payload = saved_meeting.json()
            if (
                saved_payload.get("scheduled_time") != meeting_payload.get("scheduled_time")
                or (saved_payload.get("meeting_link") or "") != (meeting_link.value or "")
            ):
                show_error(page, "Meeting save could not be confirmed from the backend.")
                return

            show_success(
                page,
                "Meeting rescheduled successfully."
                if reschedule_state["meeting_id"]
                else "Meeting scheduled successfully.",
            )
            open_dialog(
                "Meeting Saved",
                [
                    muted_text(
                        "Meeting details were saved successfully."
                    ),
                    muted_text(f"Scheduled time: {saved_payload.get('scheduled_time', 'Not set')}"),
                    muted_text(f"Google Meet link: {saved_payload.get('meeting_link', 'Not set')}"),
                ],
                [ft.TextButton("OK", on_click=lambda e: close_dialog())],
            )
            clear_schedule_form()
            load_accepted_claims()
            load_meetings()
        else:
            show_error(page, f"Could not create meeting: {response.text}")

    def create_meeting(e):
        if not is_donor:
            show_error(page, "Only donors can schedule meetings.")
            return

        if not validate_schedule_form():
            return

        show_schedule_dialog()

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
        meeting_date.on_change = refresh_schedule_validation
        meeting_time.on_change = refresh_schedule_validation
        refresh_schedule_validation(update_page=False)
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
                    ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Container(content=meeting_date, expand=True),
                                    secondary_button(
                                        "Pick Date",
                                        open_date_picker,
                                        width=160,
                                        icon=ft.Icons.CALENDAR_MONTH,
                                    ),
                                ],
                                vertical_alignment=ft.CrossAxisAlignment.END,
                            ),
                            meeting_date_error,
                        ],
                        spacing=4,
                    ),
                    ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Container(content=meeting_time, expand=True),
                                    secondary_button(
                                        "Pick Time",
                                        open_time_picker,
                                        width=160,
                                        icon=ft.Icons.SCHEDULE,
                                    ),
                                ],
                                vertical_alignment=ft.CrossAxisAlignment.END,
                            ),
                            meeting_time_error,
                        ],
                        spacing=4,
                    ),
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
            )
        ],
    )
