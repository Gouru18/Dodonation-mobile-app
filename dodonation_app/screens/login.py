# pylint: disable=E1121, E1123
import re

import flet as ft
from helpers import form_container, show_message, clear_page
from auth_api import login_user
from config import PRIMARY_GREEN, SECONDARY_GREEN, BUTTON_TEXT, INPUT_TEXT

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _extract_error_message(response, fallback_message):
    try:
        data = response.json()
    except ValueError:
        return fallback_message

    if isinstance(data, dict):
        for key in ("detail", "message", "error", "non_field_errors"):
            value = data.get(key)
            if isinstance(value, list) and value:
                return str(value[0])
            if value:
                return str(value)

        for value in data.values():
            if isinstance(value, list) and value:
                return str(value[0])
            if value:
                return str(value)

    return fallback_message


def login_screen(page, go_to_register, go_to_dashboard):
    clear_page(page)

    email = ft.TextField(label="Email", color=INPUT_TEXT, prefix_icon=ft.Icons.EMAIL)
    password = ft.TextField(label="Password", color=INPUT_TEXT, password=True, prefix_icon=ft.Icons.LOCK)

    def clear_errors():
        email.error_text = None
        password.error_text = None

    def validate_form():
        clear_errors()
        is_valid = True

        email_value = (email.value or "").strip()
        password_value = password.value or ""

        if not email_value:
            email.error_text = "Email is required"
            is_valid = False
        elif not EMAIL_PATTERN.match(email_value):
            email.error_text = "Enter a valid email address"
            is_valid = False

        if not password_value:
            password.error_text = "Password is required"
            is_valid = False

        page.update()
        return is_valid

    def login(e):
        if not validate_form():
            show_message(page, "Please fix the highlighted fields", "red")
            return

        try:
            res = login_user(email.value.strip(), password.value)

            if res.status_code == 200:
                show_message(page, "Login successful")
                go_to_dashboard()
            else:
                show_message(page, _extract_error_message(res, "Invalid credentials"), "red")

        except Exception as ex:
            print(ex)
            show_message(page, "Server error", "red")

    card = form_container("Login", [
        email,
        password,
        ft.Button(content="Login", color=BUTTON_TEXT,bgcolor=PRIMARY_GREEN, on_click=login, width=300),
        ft.TextButton("Don't have an account? Register",
                      style=ft.ButtonStyle(
                      color=SECONDARY_GREEN
                      ),
                      on_click=lambda e: go_to_register())
    ])

    page.add(
        ft.Column(
            controls=[card],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )
