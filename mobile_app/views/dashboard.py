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

    is_donor = role == "donor"
    is_ngo = role == "ngo"

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

    if is_donor:
        quick_actions = [
            primary_button("My Profile", open_profile, width=200, icon=ft.Icons.PERSON),
            secondary_button("My Donations", open_donations, width=200, icon=ft.Icons.VOLUNTEER_ACTIVISM),
            primary_button("Claim Requests", open_claims, width=200, icon=ft.Icons.ASSIGNMENT_TURNED_IN),
            secondary_button("Meetings", open_meetings, width=200, icon=ft.Icons.VIDEO_CALL),
            secondary_button("Meeting Map", open_map, width=200, icon=ft.Icons.MAP),
        ]
        welcome_subtitle = "Manage your donation posts, review incoming claims, and track meetings from one place."
        account_note = "You can create donations, manage your own posts, accept or reject NGO claims, and continue the meeting workflow."
    else:
        quick_actions = [
            primary_button("My Profile", open_profile, width=200, icon=ft.Icons.PERSON),
            secondary_button("Browse Donations", open_donations, width=200, icon=ft.Icons.VOLUNTEER_ACTIVISM),
            primary_button("My Claims", open_claims, width=200, icon=ft.Icons.ASSIGNMENT_TURNED_IN),
            secondary_button("Meetings", open_meetings, width=200, icon=ft.Icons.VIDEO_CALL),
            primary_button("Permit", open_permits, width=200, icon=ft.Icons.BADGE),
        ]
        welcome_subtitle = "Browse donation posts, track your claim requests, and manage permit approval from one place."
        account_note = "If you are an NGO, your permit review status is available in the Permit section."

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
                            muted_text(account_note),
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
