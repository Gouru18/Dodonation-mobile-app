# pylint: disable=E1121, E1123
import re

import flet as ft
from auth_api import register_user
from helpers import show_message, clear_page, form_container
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


def register_screen(page, role, go_to_otp, go_back, set_email):
    clear_page(page)

    name = ft.TextField(label="Name", color= INPUT_TEXT, prefix_icon=ft.Icons.PERSON)
    email = ft.TextField(label="Email", color= INPUT_TEXT, prefix_icon=ft.Icons.EMAIL)
    password = ft.TextField(label="Password", color= INPUT_TEXT, password=True, prefix_icon=ft.Icons.LOCK)

    def clear_errors():
        name.error_text = None
        email.error_text = None
        password.error_text = None

    def validate_form():
        clear_errors()
        is_valid = True

        name_value = (name.value or "").strip()
        email_value = (email.value or "").strip()
        password_value = password.value or ""

        if not name_value:
            name.error_text = "Name is required"
            is_valid = False
        elif len(name_value) < 2:
            name.error_text = "Name must be at least 2 characters"
            is_valid = False

        if not email_value:
            email.error_text = "Email is required"
            is_valid = False
        elif not EMAIL_PATTERN.match(email_value):
            email.error_text = "Enter a valid email address"
            is_valid = False

        if not password_value:
            password.error_text = "Password is required"
            is_valid = False
        elif len(password_value) < 8:
            password.error_text = "Password must be at least 8 characters"
            is_valid = False

        page.update()
        return is_valid

    def register(e):
        if not validate_form():
            show_message(page, "Please fix the highlighted fields", "red")
            return

        try:
            res = register_user(name.value.strip(), email.value.strip(), password.value, role)

            if res.status_code == 201:
                set_email(email.value.strip())
                show_message(page, "OTP sent")
                go_to_otp()
            else:
                show_message(page, _extract_error_message(res, "Registration failed"), "red")

        except Exception as ex:
            print(ex)
            show_message(page, "Server error", "red")

    card = form_container(f"Register ({role})", [
        name,
        email,
        password,
        ft.Button("Register", color=BUTTON_TEXT,bgcolor=PRIMARY_GREEN, width=300, on_click=register),
        ft.TextButton("Back", 
                       style=ft.ButtonStyle(
                       color=SECONDARY_GREEN
                       ),
                       on_click=lambda e: go_back())
    ])

    page.add(
        ft.Column(
            controls=[card],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )
