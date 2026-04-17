import flet as ft
from services.auth_service import AuthService
from utils.constants import PRIMARY_GREEN, SECONDARY_GREEN, BUTTON_TEXT, INPUT_TEXT
from utils.helpers import form_container, show_message


def login_view(page: ft.Page):
    email = ft.TextField(label="Email", color=INPUT_TEXT, prefix_icon=ft.icons.EMAIL)
    password = ft.TextField(label="Password", color=INPUT_TEXT, password=True, prefix_icon=ft.icons.LOCK)

    def login(e):
        try:
            response = AuthService.login(email.value, password.value)
            if response.status_code == 200:
                AuthService.set_token(response.json().get("access"))
                show_message(page, "Login successful", "green")
                page.go("/dashboard")
            else:
                show_message(page, "Invalid credentials", "red")
        except Exception as ex:
            show_message(page, f"Server error: {ex}", "red")

    card = form_container("Login", [
        email,
        password,
        ft.ElevatedButton("Login", on_click=login, bgcolor=PRIMARY_GREEN, color=BUTTON_TEXT, width=280),
        ft.TextButton("Register", on_click=lambda e: page.go("/register"), color=SECONDARY_GREEN)
    ])

    return ft.View(
        route="/",
        appbar=ft.AppBar(title=ft.Text("Donation App - Login")),
        controls=[
            ft.Container(
                expand=True,
                padding=20,
                content=ft.Column(
                    [card],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            )
        ],
    )
