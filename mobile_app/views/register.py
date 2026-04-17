import flet as ft
from services.auth_service import AuthService
from utils.constants import PRIMARY_GREEN, SECONDARY_GREEN, BUTTON_TEXT, INPUT_TEXT
from utils.helpers import form_container, show_message


def register_view(page: ft.Page):
    name = ft.TextField(label="Name", color=INPUT_TEXT, prefix_icon=ft.icons.PERSON)
    email = ft.TextField(label="Email", color=INPUT_TEXT, prefix_icon=ft.icons.EMAIL)
    password = ft.TextField(label="Password", color=INPUT_TEXT, password=True, prefix_icon=ft.icons.LOCK)

    def register(e):
        try:
            response = AuthService.register(name.value, email.value, password.value)
            if response.status_code in (200, 201):
                show_message(page, "Registration successful. Please login.", "green")
                page.go("/")
            else:
                show_message(page, f"Registration failed: {response.text}", "red")
        except Exception as ex:
            show_message(page, f"Server error: {ex}", "red")

    card = form_container("Register", [
        name,
        email,
        password,
        ft.ElevatedButton("Register", on_click=register, bgcolor=PRIMARY_GREEN, color=BUTTON_TEXT, width=280),
        ft.TextButton("Back to Login", on_click=lambda e: page.go("/"), color=SECONDARY_GREEN),
    ])

    return ft.View(
        route="/register",
        appbar=ft.AppBar(title=ft.Text("Donation App - Register")),
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
