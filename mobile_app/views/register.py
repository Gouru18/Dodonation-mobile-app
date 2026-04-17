import flet as ft
from services.auth_service import AuthService
from utils.constants import PRIMARY_GREEN, SECONDARY_GREEN, BUTTON_TEXT, INPUT_TEXT
from utils.helpers import form_container, show_message

def register_view(page: ft.Page):
    name = ft.TextField(label="Name", color=INPUT_TEXT, prefix_icon=ft.Icons.PERSON)
    email = ft.TextField(label="Email", color=INPUT_TEXT, prefix_icon=ft.Icons.EMAIL)
    password = ft.TextField(label="Password", color=INPUT_TEXT, password=True, prefix_icon=ft.Icons.LOCK)

    async def register(e):
        try:
            response = AuthService.register(name.value, email.value, password.value)
            if response.status_code in (200, 201):
                show_message(page, "Registration successful. Please login.", "green")
                await page.push_route("/")
            else:
                show_message(page, f"Registration failed: {response.text}", "red")
        except Exception as ex:
            show_message(page, f"Server error: {ex}", "red")

    async def go_back_to_login(e):
        await page.push_route("/")

    card = form_container("Register", [
        name,
        email,
        password,
        ft.Button("Register", on_click=register, bgcolor=PRIMARY_GREEN, color=BUTTON_TEXT, width=300, height=45),
        ft.TextButton(
            "Back to Login",
            on_click=go_back_to_login,
            style=ft.ButtonStyle(
                color=SECONDARY_GREEN
            ),
        ),
    ])

    return ft.View(
        route="/register",
        appbar=ft.AppBar(title=ft.Text("Donation App - Register")),
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
