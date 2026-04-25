import asyncio
import re
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

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _inline_error():
    return ft.Text("", color="#B42318", size=12, visible=False)


def _field_block(field, error_label):
    return ft.Column([field, error_label], spacing=4)


def _set_error(field, error_label, message):
    field.error_text = message
    error_label.value = message or ""
    error_label.visible = bool(message)


def _validate_login_identifier(value):
    value = (value or "").strip()
    if not value:
        return "Username or email is required."
    if "@" in value and not EMAIL_PATTERN.match(value):
        return "Enter a valid email address."
    return None


def _validate_password(value):
    value = value or ""
    if not value:
        return "Password is required."
    if len(value) < 6:
        return "Password must be at least 6 characters."
    return None


def _is_invalid_credentials_response(status_code, message):
    normalized = (message or "").strip().lower()
    if status_code in (400, 401):
        if not normalized:
            return True
        invalid_markers = (
            "invalid credentials",
            "invalid username",
            "invalid email",
            "incorrect",
            "bad request",
            "unable to log in",
            "no active account",
        )
        return any(marker in normalized for marker in invalid_markers)
    return False


def login_view(page: ft.Page):
    identifier = auth_input("Username or Email", ft.Icons.PERSON)
    password = auth_input("Password", ft.Icons.LOCK, password=True)
    identifier_error = _inline_error()
    password_error = _inline_error()
    feedback_message = ft.Text("", color="#B42318", size=13, visible=False)
    feedback_box = ft.Container(
        visible=False,
        padding=12,
        border_radius=14,
        bgcolor="#FEF3F2",
        border=ft.Border.all(1, "#FECACA"),
        content=feedback_message,
    )
    submit_button = primary_button("Login", None)

    def clear_feedback():
        feedback_message.value = ""
        feedback_box.visible = False

    def show_feedback(message, color="#B42318", bg="#FEF3F2", border="#FECACA"):
        feedback_message.value = message
        feedback_message.color = color
        feedback_box.bgcolor = bg
        feedback_box.border = ft.Border.all(1, border)
        feedback_box.visible = True
        page.update()

    def refresh_form(*_, update_page=True):
        identifier_message = _validate_login_identifier(identifier.value)
        password_message = _validate_password(password.value)
        _set_error(identifier, identifier_error, identifier_message)
        _set_error(password, password_error, password_message)
        clear_feedback()
        submit_button.disabled = bool(identifier_message or password_message)
        if update_page:
            page.update()

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
            refresh_form()
            if submit_button.disabled:
                show_feedback("Please enter a valid username/email and password.")
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
                await AuthService.persist_session(page)
                show_feedback(
                    "Login successful.",
                    color="#166534",
                    bg="#ECFDF3",
                    border="#ABEFC6",
                )
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
                elif response.status_code in (400, 401) or _is_invalid_credentials_response(response.status_code, message):
                    message = "Incorrect username/email or password."

                password_error.value = message
                password_error.visible = True
                show_feedback(message)

        except Exception as ex:
            show_feedback(f"Error: {str(ex)}")

    async def go_to_register(e):
        await page.push_route("/role-selection")

    identifier.on_change = refresh_form
    password.on_change = refresh_form
    submit_button.on_click = login
    submit_button.disabled = True

    card = form_container(
        "Login",
        [
            muted_text("Welcome back. Sign in to manage donations, claims, permits, meetings, and messages."),
            feedback_box,
            _field_block(identifier, identifier_error),
            _field_block(password, password_error),
            submit_button,
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

    refresh_form(update_page=False)
    return auth_scaffold(page, "/", "Dodonation Login", card)
