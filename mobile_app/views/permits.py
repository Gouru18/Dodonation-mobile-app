import asyncio
import os
import flet as ft

from services.permit_service import PermitService
from utils.helpers import (
    build_appbar,
    centered_content,
    page_container,
    section_card,
    primary_button,
    secondary_button,
    muted_text,
    status_chip,
    show_error,
    show_success,
)


def permits_view(page: ft.Page):
    permit_path = {"value": None}
    permit_file_label = ft.Text("No permit selected", color="#6B7280")
    permit_summary = ft.Text("", color="#4B5563")
    permit_list = ft.Column(spacing=10)

    permit_picker = ft.FilePicker()
    page.overlay.append(permit_picker)

    def display_status(value):
        return PermitService.display_status(value)

    def status_color(value):
        normalized = (value or "").lower()
        return {
            "pending": "#B54708",
            "approved": "#027A48",
            "rejected": "#B42318",
            "unknown": "#667085",
        }.get(normalized, "#667085")

    def latest_status_label(permit):
        if not permit:
            return "unknown"
        return (permit.get("status") or "unknown").lower()

    def sort_key(permit):
        return (
            permit.get("reviewed_at") or "",
            permit.get("submitted_at") or "",
        )

    def load_permits():
        response = PermitService.get_my_permit()
        permit_list.controls.clear()

        if response.status_code != 200:
            permit_summary.value = f"Could not load permit info: {response.text}"
            page.update()
            return

        permits = response.json()

        if not permits:
            permit_summary.value = "No permit uploaded yet."
        else:
            permits = sorted(permits, key=sort_key, reverse=True)
            latest = permits[0]
            latest_status = latest_status_label(latest)

            permit_summary.value = "Your latest permit submission is shown below."

            permit_list.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(
                                        "Latest Permit Status",
                                        size=18,
                                        weight=ft.FontWeight.BOLD,
                                        color="#1F2937",
                                        expand=True,
                                    ),
                                    status_chip(
                                        display_status(latest_status),
                                        color=status_color(latest_status),
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            muted_text(f"Submitted: {latest.get('submitted_at', 'N/A')}"),
                            muted_text(
                                f"Reviewed: {latest.get('reviewed_at', 'Not reviewed yet')}"
                            ),
                            muted_text(
                                f"Rejection reason: {latest.get('rejection_reason') or 'None'}"
                            ),
                        ],
                        spacing=8,
                    ),
                    padding=16,
                    border=ft.Border.all(1, "#D6E2D3"),
                    border_radius=18,
                    bgcolor="#FFFEFB",
                )
            )

            if len(permits) > 1:
                for permit in permits[1:]:
                    status_value = (permit.get("status") or "unknown").lower()
                    permit_list.controls.append(
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Row(
                                        [
                                            ft.Text(
                                                "Previous Submission",
                                                weight=ft.FontWeight.BOLD,
                                                color="#1F2937",
                                                expand=True,
                                            ),
                                            status_chip(
                                                display_status(status_value),
                                                color=status_color(status_value),
                                            ),
                                        ],
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    ),
                                    muted_text(f"Submitted: {permit.get('submitted_at', 'N/A')}"),
                                    muted_text(
                                        f"Reviewed: {permit.get('reviewed_at', 'Not reviewed yet')}"
                                    ),
                                    muted_text(
                                        f"Rejection reason: {permit.get('rejection_reason') or 'None'}"
                                    ),
                                ],
                                spacing=6,
                            ),
                            padding=14,
                            border=ft.Border.all(1, "#D6E2D3"),
                            border_radius=16,
                            bgcolor="#FFFFFF",
                        )
                    )

        page.update()

    async def choose_permit(e):
        selected = await permit_picker.pick_files(
            dialog_title="Choose NGO permit file",
            allow_multiple=False,
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["pdf", "png", "jpg", "jpeg"],
        )

        if selected and selected.files:
            selected_file = selected.files[0]
            permit_path["value"] = selected_file.path
            permit_file_label.value = selected_file.name or os.path.basename(selected_file.path)
        else:
            permit_path["value"] = None
            permit_file_label.value = "No permit selected"

        page.update()

    async def upload_permit(e):
        if not permit_path["value"]:
            show_error(page, "Choose a permit file first.")
            return

        response = await asyncio.to_thread(
            PermitService.upload_permit,
            permit_path["value"],
        )

        if response.status_code in (200, 201):
            show_success(page, "Permit uploaded.")
            permit_path["value"] = None
            permit_file_label.value = "No permit selected"
            load_permits()
        else:
            show_error(page, f"Could not upload permit: {response.text}")

    async def go_back(e):
        await page.push_route("/dashboard")

    load_permits()

    return ft.View(
        route="/permits",
        appbar=build_appbar("NGO Permit", go_back),
        controls=[
            page_container(
                centered_content(
                    section_card(
                        "Permit Upload",
                        [
                            muted_text(
                                "Upload the registration permit that admins will review before activating the NGO account."
                            ),
                            permit_summary,
                            ft.Container(
                                padding=16,
                                border_radius=16,
                                bgcolor="#FFFFFF",
                                border=ft.Border.all(1, "#D6E2D3"),
                                content=ft.Column(
                                    [
                                        ft.Row(
                                            [
                                                secondary_button(
                                                    "Choose Permit",
                                                    choose_permit,
                                                    width=170,
                                                    icon=ft.Icons.UPLOAD_FILE,
                                                ),
                                                permit_file_label,
                                            ],
                                            wrap=True,
                                            spacing=12,
                                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                        ),
                                        ft.Row(
                                            [
                                                primary_button(
                                                    "Upload Permit",
                                                    upload_permit,
                                                    width=170,
                                                    icon=ft.Icons.CLOUD_UPLOAD,
                                                ),
                                                secondary_button(
                                                    "Refresh",
                                                    lambda e: load_permits(),
                                                    width=140,
                                                    icon=ft.Icons.REFRESH,
                                                ),
                                            ],
                                            wrap=True,
                                            spacing=12,
                                        ),
                                    ],
                                    spacing=12,
                                ),
                            ),
                        ],
                    ),
                    section_card(
                        "Permit History",
                        [permit_list],
                        subtitle="Previous submissions and review results are shown below.",
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
                ),
            ),
        ],
    )