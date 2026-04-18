import flet as ft

from services.permit_service import PermitService
from utils.constants import PRIMARY_GREEN, SECONDARY_GREEN, BUTTON_TEXT, INPUT_TEXT
from utils.helpers import show_message


def permits_view(page: ft.Page):
    permit_path = ft.TextField(label="Permit File Path", color=INPUT_TEXT)
    permit_status = ft.Text("")
    permit_list = ft.Column(spacing=10)

    def load_permits():
        response = PermitService.get_my_permit()
        permit_list.controls.clear()

        if response.status_code != 200:
            permit_status.value = f"Could not load permit info: {response.text}"
            page.update()
            return

        permits = response.json()
        if not permits:
            permit_status.value = "No permit uploaded yet."
        else:
            latest = permits[0]
            permit_status.value = f"Latest status: {latest.get('status', 'unknown')}"
            for permit in permits:
                permit_list.controls.append(
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(f"Status: {permit.get('status', 'unknown')}", weight=ft.FontWeight.BOLD),
                                ft.Text(f"Submitted: {permit.get('submitted_at', '')}"),
                                ft.Text(f"Rejection reason: {permit.get('rejection_reason') or 'None'}"),
                            ],
                            spacing=6,
                        ),
                        padding=12,
                        border=ft.border.all(1, "#d9d9d9"),
                        border_radius=12,
                    )
                )
        page.update()

    def upload_permit(e):
        if not permit_path.value:
            show_message(page, "Enter the local file path to the permit first.", "red")
            return

        response = PermitService.upload_permit(permit_path.value)
        if response.status_code in (200, 201):
            show_message(page, "Permit uploaded.", "green")
            permit_path.value = ""
            load_permits()
        else:
            show_message(page, f"Could not upload permit: {response.text}", "red")

    async def go_back(e):
        await page.push_route("/dashboard")

    load_permits()

    return ft.View(
        route="/permits",
        appbar=ft.AppBar(title=ft.Text("NGO Permit")),
        controls=[
            ft.Container(
                expand=True,
                padding=20,
                content=ft.Column(
                    [
                        permit_status,
                        permit_path,
                        ft.Row(
                            [
                                ft.Button("Upload Permit", on_click=upload_permit, bgcolor=PRIMARY_GREEN, color=BUTTON_TEXT),
                                ft.Button("Refresh", on_click=lambda e: load_permits(), bgcolor=SECONDARY_GREEN, color=BUTTON_TEXT),
                            ]
                        ),
                        permit_list,
                        ft.Button("Back", on_click=go_back, bgcolor="#666666", color=BUTTON_TEXT),
                    ],
                    spacing=15,
                    expand=True,
                ),
            )
        ],
    )
