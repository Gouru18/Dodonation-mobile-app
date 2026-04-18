import flet as ft
from services.auth_service import AuthService
from utils.constants import PRIMARY_GREEN, SECONDARY_GREEN, BUTTON_TEXT

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
        ft.Button("My Profile", on_click=open_profile, bgcolor=PRIMARY_GREEN, color=BUTTON_TEXT),
        ft.Button("Donations", on_click=open_donations, bgcolor=SECONDARY_GREEN, color=BUTTON_TEXT),
        ft.Button("Claims", on_click=open_claims, bgcolor=PRIMARY_GREEN, color=BUTTON_TEXT),
        ft.Button("Meetings", on_click=open_meetings, bgcolor=SECONDARY_GREEN, color=BUTTON_TEXT),
    ]

    if role == "ngo":
        action_buttons.append(ft.Button("Permit", on_click=open_permits, bgcolor=PRIMARY_GREEN, color=BUTTON_TEXT))

    return ft.View(
        route="/dashboard",
        appbar=ft.AppBar(title=ft.Text("Donation App - Dashboard")),
        controls=[
            ft.Container(
                expand=True,
                padding=20,
                content=ft.Column(
                    [
                        ft.Text("Welcome to DoDonation", size=26, weight=ft.FontWeight.BOLD),
                        ft.Text(user.get("email", ""), size=14),
                        ft.Text(f"Role: {role or 'unknown'}", size=14),
                        *action_buttons,
                        ft.Button("Open Chatbot", on_click=open_chatbot, bgcolor=SECONDARY_GREEN, color=BUTTON_TEXT),
                        ft.Button("View Map", on_click=view_map, bgcolor=PRIMARY_GREEN, color=BUTTON_TEXT),
                        ft.Button("Logout", on_click=logout, bgcolor="#666", color=BUTTON_TEXT),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20,
                ),
            )
        ],
    )
