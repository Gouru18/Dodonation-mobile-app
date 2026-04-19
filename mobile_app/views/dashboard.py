import flet as ft
from services.auth_service import AuthService
from utils.helpers import (
    build_appbar,
    page_container,
    centered_content,
    section_card,
    primary_button,
    secondary_button,
    subtle_text_button,
    muted_text,
    status_chip,
)
from views.admin_panel import admin_panel_view


def dashboard_view(page: ft.Page):
    user = AuthService.user or {}
    role = user.get("role", "")

    if role == "admin" or user.get("is_staff") or user.get("is_superuser"):
        return admin_panel_view(page)

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

    async def open_map(e):
        await page.push_route("/map")

    async def logout(e):
        AuthService.logout()
        await page.push_route("/")

    role_label = role.capitalize() if role else "Unknown"

    quick_actions = [
        primary_button("My Profile", open_profile, width=180, icon=ft.Icons.PERSON),
        secondary_button("Donations", open_donations, width=180, icon=ft.Icons.VOLUNTEER_ACTIVISM),
        primary_button("Claims", open_claims, width=180, icon=ft.Icons.ASSIGNMENT_TURNED_IN),
        secondary_button("Meetings", open_meetings, width=180, icon=ft.Icons.VIDEO_CALL),
        secondary_button("Meeting Map", open_map, width=180, icon=ft.Icons.MAP),
    ]

    if role == "ngo":
        quick_actions.append(
            primary_button("Permit", open_permits, width=180, icon=ft.Icons.BADGE)
        )

    welcome_subtitle = (
        "Track your donations, claims, meetings, and permit status from one place."
        if role == "ngo"
        else "Manage your donations, received claims, and meetings from one place."
    )

    return ft.View(
        route="/dashboard",
        appbar=build_appbar("Dashboard"),
        controls=[
            page_container(
                centered_content(
                    section_card(
                        "Welcome to Dodonation",
                        [
                            ft.Text(
                                user.get("username", "") or user.get("email", "User"),
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color="#1F2937",
                            ),
                            muted_text(f"Signed in as: {user.get('email', 'No email')}"),
                            status_chip(f"Role: {role_label}", color="#1D4ED8"),
                        ],
                        subtitle=welcome_subtitle,
                    ),
                    section_card(
                        "Quick Actions",
                        [
                            ft.ResponsiveRow(
                                [
                                    ft.Container(content=btn, col={"sm": 12, "md": 6})
                                    for btn in quick_actions
                                ],
                                spacing=12,
                                run_spacing=12,
                            )
                        ],
                        subtitle="Use these shortcuts to move around the app quickly.",
                    ),
                    section_card(
                        "Account",
                        [
                            muted_text(
                                "If you are an NGO, your permit status and approval workflow are available in the permit section."
                            ),
                            ft.Row(
                                [subtle_text_button("Logout", logout)],
                                alignment=ft.MainAxisAlignment.END,
                            ),
                        ],
                    ),
                )
            ),
        ],
    )
