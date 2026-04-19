import flet as ft
from utils.constants import PRIMARY_GREEN, SECONDARY_GREEN
from utils.helpers import auth_scaffold, form_container, role_card, subtle_text_button, muted_text


def role_selection_view(page: ft.Page):
    async def select_donor(e):
        await page.push_route("/register/donor")

    async def select_ngo(e):
        await page.push_route("/register/ngo")

    async def go_back_to_login(e):
        await page.push_route("/")

    card = form_container(
        "Join Dodonation",
        [
            muted_text("Choose the account type that best matches how you will use the app."),
            role_card(
                "Donor",
                "Post donations, manage claims, schedule meetings, and set handoff locations.",
                ft.Icons.VOLUNTEER_ACTIVISM,
                select_donor,
                PRIMARY_GREEN,
            ),
            role_card(
                "NGO",
                "Claim donations, upload permits, coordinate with donors, and manage meetings.",
                ft.Icons.BUSINESS,
                select_ngo,
                SECONDARY_GREEN,
            ),
            ft.Row(
                [subtle_text_button("Back to Login", go_back_to_login)],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
        subtitle="Start by selecting your role.",
    )

    return auth_scaffold(page, "/role-selection", "Choose Your Role", card)