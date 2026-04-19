import asyncio
import flet as ft
from services.auth_service import AuthService
from utils.helpers import (
    auth_scaffold,
    form_container,
    auth_input,
    primary_button,
    subtle_text_button,
    muted_text,
    show_error,
    show_success,
)


def login_view(page: ft.Page):
    identifier = auth_input("Username or Email", ft.Icons.PERSON)
    password = auth_input("Password", ft.Icons.LOCK, password=True)

    def _extract_error_message(error_data):
        if isinstance(error_data, dict):
            if "message" in error_data:
                return str(error_data["message"])
            if "detail" in error_data:
                return str(error_data["detail"])
            if "non_field_errors" in error_data and error_data["non_field_errors"]:
                return str(error_data["non_field_errors"][0])

            parts = []
            for key, value in error_data.items():
                if isinstance(value, list):
                    parts.append(f"{key}: {', '.join(str(v) for v in value)}")
                else:
                    parts.append(f"{key}: {value}")
            if parts:
                return " | ".join(parts)

        return "Invalid credentials"

    async def login(e):
        try:
            if not identifier.value or not password.value:
                show_error(page, "Please enter your username/email and password")
                return

            response = await asyncio.to_thread(
                AuthService.login,
                identifier.value,
                password.value
            )

            if response.status_code == 200:
                data = response.json()
                AuthService.set_token(data.get("access"))
                AuthService.set_user(data.get("user", {}))
                show_success(page, "Login successful")

                user = data.get("user", {}) or {}
                if user.get("role") == "admin" or user.get("is_staff") or user.get("is_superuser"):
                    await page.push_route("/admin-panel")
                else:
                    await page.push_route("/dashboard")
            else:
                try:
                    error_data = response.json()
                except ValueError:
                    error_data = {"detail": response.text or "Invalid credentials"}

                message = _extract_error_message(error_data)

                # Make NGO inactive message cleaner for users
                if "not active" in message.lower():
                    message = "Your NGO account is pending admin approval. You can access the app only after your permit has been reviewed."

                show_error(page, message)

        except Exception as ex:
            show_error(page, f"Error: {str(ex)}")

    async def go_to_register(e):
        await page.push_route("/role-selection")

    card = form_container(
        "Login",
        [
            muted_text("Welcome back. Sign in to manage donations, claims, permits, meetings, and messages."),
            identifier,
            password,
            primary_button("Login", login),
            ft.Row(
                [
                    muted_text("Don’t have an account?", size=14),
                    subtle_text_button("Register", go_to_register),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=6,
            ),
        ],
        subtitle="Access your donor, NGO, or admin workspace.",
    )

    return auth_scaffold(page, "/", "Dodonation Login", card)