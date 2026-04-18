import flet as ft
from services.auth_service import AuthService
from utils.constants import PRIMARY_GREEN, SECONDARY_GREEN, BUTTON_TEXT
from utils.helpers import build_appbar, page_container, section_card

def dashboard_view(page: ft.Page):
    user = AuthService.user or {}
    role = user.get("role", "")

    async def open_donations(e):
        await page.push_route("/donations")

    async def open_claims(e):
        await page.push_route("/claims")

    async def open_meetings(e):
        await page.push_route("/meetings")

    async def open_profile(e):
        await page.push_route("/profile")

    async def open_permits(e):
        await page.push_route("/permits")

    async def open_chatbot(e):
        await page.push_route("/chatbot")

    async def view_map(e):
        await page.push_route("/map")

    async def logout(e):
        AuthService.logout()
        await page.push_route("/")

    action_buttons = [
        ft.Button("My Profile", on_click=open_profile, bgcolor=PRIMARY_GREEN, color=BUTTON_TEXT, width=180),
        ft.Button("Donations", on_click=open_donations, bgcolor=SECONDARY_GREEN, color=BUTTON_TEXT, width=180),
        ft.Button("Claims", on_click=open_claims, bgcolor=PRIMARY_GREEN, color=BUTTON_TEXT, width=180),
        ft.Button("Meetings", on_click=open_meetings, bgcolor=SECONDARY_GREEN, color=BUTTON_TEXT, width=180),
    ]

    if role == "ngo":
        action_buttons.append(ft.Button("Permit", on_click=open_permits, bgcolor=PRIMARY_GREEN, color=BUTTON_TEXT, width=180))

    return ft.View(
        route="/dashboard",
        appbar=build_appbar("Dashboard"),
        controls=[
            page_container(
                section_card(
                    "Welcome to Dodonation",
                    [
                        ft.Text(user.get("username", "") or user.get("email", ""), size=16),
                        ft.Text(f"Role: {role or 'unknown'}", size=14, color="#4B5563"),
                    ],
                    subtitle="Manage your donations, claims, meetings, and support tools from one place.",
                ),
                section_card(
                    "Quick Actions",
                    [
                        ft.Row(action_buttons[:2], wrap=True, spacing=12),
                        ft.Row(action_buttons[2:], wrap=True, spacing=12),
                        ft.Row(
                            [
                                ft.Button("Open Chatbot", on_click=open_chatbot, bgcolor=SECONDARY_GREEN, color=BUTTON_TEXT, width=180),
                                ft.Button("Meeting Map", on_click=view_map, bgcolor=PRIMARY_GREEN, color=BUTTON_TEXT, width=180),
                            ],
                            wrap=True,
                            spacing=12,
                        ),
                    ],
                ),
                ft.Row(
                    [ft.Button("Logout", on_click=logout, bgcolor="#666666", color=BUTTON_TEXT, width=160)],
                    alignment=ft.MainAxisAlignment.END,
                ),
            ),
        ],
    )
