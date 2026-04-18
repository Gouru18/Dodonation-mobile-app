import flet as ft
from utils.constants import PRIMARY_GREEN, SECONDARY_GREEN, BUTTON_TEXT, INPUT_TEXT
from utils.helpers import form_container


def role_selection_view(page: ft.Page):
    """Screen for selecting registration role (Donor or NGO)"""

    async def select_donor(e):
        await page.push_route("/register/donor")

    async def select_ngo(e):
        await page.push_route("/register/ngo")

    async def go_back_to_login(e):
        await page.push_route("/")

    card = form_container("Join Dodonation", [
        ft.Text("Select your role to get started:", size=16, weight="bold"),
        ft.Divider(),
        ft.Button(
            "Register as Donor",
            on_click=select_donor,
            bgcolor=PRIMARY_GREEN,
            color=BUTTON_TEXT,
            width=300,
            height=45
        ),
        ft.SizedBox(height=10),
        ft.Button(
            "Register as NGO",
            on_click=select_ngo,
            bgcolor=PRIMARY_GREEN,
            color=BUTTON_TEXT,
            width=300,
            height=45
        ),
        ft.SizedBox(height=15),
        ft.TextButton(
            "Back to Login",
            on_click=go_back_to_login,
            style=ft.ButtonStyle(color=SECONDARY_GREEN),
        ),
    ])

    return ft.View(
        route="/role-selection",
        appbar=ft.AppBar(title=ft.Text("Donation App - Select Role")),
        controls=[
            ft.Container(
                expand=True,
                padding=20,
                alignment=ft.Alignment.CENTER,
                content=ft.Column(
                    [card],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            )
        ],
    )
