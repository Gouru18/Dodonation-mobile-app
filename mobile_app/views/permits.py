import asyncio
import flet as ft

from services.permit_service import PermitService
from utils.constants import PRIMARY_GREEN, SECONDARY_GREEN, BUTTON_TEXT, INPUT_TEXT
from utils.helpers import build_appbar, centered_content, page_container, section_card, show_message


def permits_view(page: ft.Page):
    permit_path = {"value": None}
    permit_file_label = ft.Text("No permit selected", color="#6B7280")
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
                        border=ft.Border.all(1, "#d9d9d9"),
                        border_radius=12,
                        bgcolor="#FFFEFB",
                    )
                )
        page.update()

    async def choose_permit(e):
        def choose_file():
            try:
                import os
                import tkinter as tk
                from tkinter import filedialog

                root = tk.Tk()
                root.withdraw()
                root.attributes("-topmost", True)
                file_path = filedialog.askopenfilename(
                    title="Choose NGO permit file",
                    filetypes=[
                        ("Documents", "*.pdf *.png *.jpg *.jpeg"),
                        ("All files", "*.*"),
                    ],
                )
                root.destroy()
                return file_path
            except Exception:
                return None

        file_path = await asyncio.to_thread(choose_file)
        if file_path:
            import os
            permit_path["value"] = file_path
            permit_file_label.value = os.path.basename(file_path)
        else:
            permit_file_label.value = "No permit selected"
        page.update()

    async def upload_permit(e):
        if not permit_path["value"]:
            show_message(page, "Choose a permit file first.", "red")
            return

        response = await asyncio.to_thread(PermitService.upload_permit, permit_path["value"])
        if response.status_code in (200, 201):
            show_message(page, "Permit uploaded.", "green")
            permit_path["value"] = None
            permit_file_label.value = "No permit selected"
            load_permits()
        else:
            show_message(page, f"Could not upload permit: {response.text}", "red")

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
                        "Permit Status",
                        [
                            permit_status,
                            ft.Row(
                                [
                                    ft.Button("Choose Permit", on_click=choose_permit, bgcolor=SECONDARY_GREEN, color=BUTTON_TEXT),
                                    permit_file_label,
                                ],
                                wrap=True,
                                spacing=12,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            ft.Row(
                                [
                                    ft.Button("Upload Permit", on_click=upload_permit, bgcolor=PRIMARY_GREEN, color=BUTTON_TEXT),
                                    ft.Button("Refresh", on_click=lambda e: load_permits(), bgcolor=SECONDARY_GREEN, color=BUTTON_TEXT),
                                ],
                                wrap=True,
                                spacing=12,
                            ),
                        ],
                        subtitle="Upload the registration permit that admins will review before activating the NGO account.",
                    ),
                    section_card("Previous Submissions", [permit_list]),
                    ft.Row(
                        [ft.Button("Back", on_click=go_back, bgcolor="#666666", color=BUTTON_TEXT, width=140)],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                ),
            ),
        ],
    )
