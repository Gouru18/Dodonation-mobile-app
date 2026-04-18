import asyncio
import flet as ft
from services.auth_service import AuthService
from utils.constants import PRIMARY_GREEN, SECONDARY_GREEN, BUTTON_TEXT, INPUT_TEXT
from utils.helpers import auth_scaffold, form_container, show_message


def login_view(page: ft.Page):
    identifier = ft.TextField(label="Username or Email", color=INPUT_TEXT, prefix_icon=ft.Icons.PERSON)
    password = ft.TextField(label="Password", color=INPUT_TEXT, password=True, prefix_icon=ft.Icons.LOCK)

    def _extract_error_message(error_data):
        if isinstance(error_data, dict):
            if "message" in error_data:
                return str(error_data["message"])
            if "detail" in error_data:
                return str(error_data["detail"])
            if "non_field_errors" in error_data and error_data["non_field_errors"]:
                return str(error_data["non_field_errors"][0])
            return " | ".join(
                f"{key}: {', '.join(value) if isinstance(value, list) else value}"
                for key, value in error_data.items()
            )
        return str(error_data)

    async def login(e):
        try:
            if not identifier.value or not password.value:
                show_message(page, "Please enter your username/email and password", "red")
                return
            
            response = await asyncio.to_thread(AuthService.login, identifier.value, password.value)
            if response.status_code == 200:
                data = response.json()
                AuthService.set_token(data.get("access"))
                AuthService.set_user(data.get("user", {}))
                show_message(page, "Login successful", "green")
                user = data.get("user", {}) or {}
                if user.get("role") == "admin" or user.get("is_staff") or user.get("is_superuser"):
                    await page.push_route("/admin-panel")
                else:
                    await page.push_route("/dashboard")
            else:
                try:
                    error_data = response.json()
                except ValueError:
                    error_data = {"detail": response.text}
                error_msg = _extract_error_message(error_data) or 'Invalid credentials'
                show_message(page, error_msg, "red")
        except Exception as ex:
            show_message(page, f"Error: {str(ex)}", "red")

    async def go_to_register(e):
        await page.push_route("/role-selection")

    card = form_container("Login", [
        ft.Text("Welcome back. Sign in to manage donations, claims, and meetings.", size=14, color="#4B5563"),
        identifier,
        password,
        ft.Button(
            "Login",
            on_click=login,
            width=300,
            height=45,
            style=ft.ButtonStyle(
                bgcolor=PRIMARY_GREEN,
                color=BUTTON_TEXT
            )
        ),
        ft.Row(
            [
                ft.Text("If you don't have an account:", size=14, color="#666666"),
                ft.TextButton(
                    "Register",
                    on_click=go_to_register,
                    style=ft.ButtonStyle(
                        color=SECONDARY_GREEN
                    )
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=6,
        )
    ])

    return auth_scaffold(page, "/", "Dodonation Login", card)
