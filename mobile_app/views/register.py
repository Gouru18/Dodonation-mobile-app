import asyncio
import re
import flet as ft
from services.auth_service import AuthService
from utils.app_state import AppState
from utils.helpers import (
    auth_scaffold,
    form_container,
    auth_input,
    primary_button,
    secondary_button,
    subtle_text_button,
    muted_text,
    status_chip,
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


def _format_error_message(error_data):
    if isinstance(error_data, dict):
        if error_data.get("message"):
            return str(error_data["message"])
        parts = []
        for key, value in error_data.items():
            if key == "errors":
                continue
            if isinstance(value, list):
                parts.append(f"{key}: {', '.join(str(item) for item in value)}")
            else:
                parts.append(f"{key}: {value}")
        return " | ".join(parts)
    return str(error_data)


def _validate_required(value, label):
    if not (value or "").strip():
        return f"{label} is required."
    return None


def _validate_email(value):
    value = (value or "").strip()
    if not value:
        return "Email is required."
    if not EMAIL_PATTERN.match(value):
        return "Enter a valid email address."
    return None

def _validate_password(value):
    value = value or ""
    if not value:
        return "Password is required."
    if len(value) < 8:
        return "Password must be at least 8 characters."
    return None

def _validate_confirm_password(password_value, confirm_value):
    if not (confirm_value or ""):
        return "Confirm password is required."
    if (password_value or "") != (confirm_value or ""):
        return "Passwords do not match."
    return None

def register_donor_view(page: ft.Page):
    username = auth_input("Username", ft.Icons.PERSON)
    full_name = auth_input("Full Name", ft.Icons.BADGE)
    email = auth_input("Email", ft.Icons.EMAIL)
    phone = auth_input("Phone (Optional)", ft.Icons.PHONE)
    password = auth_input("Password", ft.Icons.LOCK, password=True)
    confirm_password = auth_input("Confirm Password", ft.Icons.LOCK_OUTLINE, password=True)
    username_error = _inline_error()
    full_name_error = _inline_error()
    email_error = _inline_error()
    password_error = _inline_error()
    confirm_password_error = _inline_error()
    submit_button = primary_button("Create Donor Account", None)

    def refresh_form(*_, update_page=True):
        username_message = _validate_required(username.value, "Username")
        full_name_message = _validate_required(full_name.value, "Full name")
        email_message = _validate_email(email.value)
        password_message = _validate_password(password.value)
        confirm_password_message = _validate_confirm_password(password.value, confirm_password.value)
        _set_error(username, username_error, username_message)
        _set_error(full_name, full_name_error, full_name_message)
        _set_error(email, email_error, email_message)
        _set_error(password, password_error, password_message)
        _set_error(confirm_password, confirm_password_error, confirm_password_message)
        submit_button.disabled = any(
            [
                username_message,
                full_name_message,
                email_message,
                password_message,
                confirm_password_message,
            ]
        )
        if update_page:
            page.update()

    async def register(e):
        try:
            refresh_form()
            if submit_button.disabled:
                show_error(page, "Please fill all required fields correctly")
                return

            response = await asyncio.to_thread(
                AuthService.register_donor,
                username=username.value,
                email=email.value,
                password=password.value,
                full_name=full_name.value,
                phone=phone.value,
            )

            if response.status_code in (200, 201):
                show_success(page, "Registration successful! Check your email for OTP.")
                AppState.pending_otp_email = email.value
                await page.push_route("/otp")
            else:
                try:
                    error_data = response.json()
                except ValueError:
                    error_data = {"detail": response.text}
                error_msg = error_data.get("detail") or _format_error_message(error_data)
                show_error(page, f"Registration failed: {error_msg}")
        except Exception as ex:
            show_error(page, f"Error: {str(ex)}")

    async def go_back(e):
        await page.push_route("/role-selection")

    username.on_change = refresh_form
    full_name.on_change = refresh_form
    email.on_change = refresh_form
    password.on_change = refresh_form
    confirm_password.on_change = refresh_form
    submit_button.on_click = register
    submit_button.disabled = True

    card = form_container(
        "Register as Donor",
        [
            muted_text("Create a donor account to post donations and manage handoff coordination."),
            _field_block(username, username_error),
            _field_block(full_name, full_name_error),
            _field_block(email, email_error),
            phone,
            _field_block(password, password_error),
            _field_block(confirm_password, confirm_password_error),
            submit_button,
            ft.Row(
                [subtle_text_button("Back", go_back)],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
        subtitle="Donors can create donations, accept claims, and schedule meetings.",
    )

    refresh_form(update_page=False)
    return auth_scaffold(page, "/register/donor", "Donor Registration", card)


def register_ngo_view(page: ft.Page):
    username = auth_input("Username", ft.Icons.PERSON)
    organization_name = auth_input("Organization Name", ft.Icons.BUSINESS)
    email = auth_input("Email", ft.Icons.EMAIL)
    registration_number = auth_input("Registration Number (Optional)", ft.Icons.NUMBERS)
    phone = auth_input("Phone (Optional)", ft.Icons.PHONE)
    password = auth_input("Password", ft.Icons.LOCK, password=True)
    confirm_password = auth_input("Confirm Password", ft.Icons.LOCK_OUTLINE, password=True)
    username_error = _inline_error()
    organization_name_error = _inline_error()
    email_error = _inline_error()
    password_error = _inline_error()
    confirm_password_error = _inline_error()
    permit_error = _inline_error()
    submit_button = primary_button("Create NGO Account", None)

    permit_file_label = ft.Text("No permit selected", color="#6B7280")
    selected_permit_path = {"value": None}

    def refresh_form(*_, update_page=True):
        username_message = _validate_required(username.value, "Username")
        organization_name_message = _validate_required(organization_name.value, "Organization name")
        email_message = _validate_email(email.value)
        password_message = _validate_password(password.value)
        confirm_password_message = _validate_confirm_password(password.value, confirm_password.value)
        permit_message = None if selected_permit_path["value"] else "Permit document is required."
        _set_error(username, username_error, username_message)
        _set_error(organization_name, organization_name_error, organization_name_message)
        _set_error(email, email_error, email_message)
        _set_error(password, password_error, password_message)
        _set_error(confirm_password, confirm_password_error, confirm_password_message)
        permit_error.value = permit_message or ""
        permit_error.visible = bool(permit_message)
        submit_button.disabled = any(
            [
                username_message,
                organization_name_message,
                email_message,
                password_message,
                confirm_password_message,
                permit_message,
            ]
        )
        if update_page:
            page.update()

    async def pick_permit(e):
        def choose_file():
            try:
                import os
                import tkinter as tk
                from tkinter import filedialog

                root = tk.Tk()
                root.withdraw()
                root.attributes("-topmost", True)
                file_path = filedialog.askopenfilename(
                    title="Choose NGO permit file",
                    filetypes=[
                        ("Documents", "*.pdf *.png *.jpg *.jpeg"),
                        ("All files", "*.*"),
                    ],
                )
                root.destroy()
                return file_path
            except Exception:
                return None

        file_path = await asyncio.to_thread(choose_file)
        if file_path:
            import os
            selected_permit_path["value"] = file_path
            permit_file_label.value = os.path.basename(file_path)
        else:
            permit_file_label.value = "No permit selected"
        refresh_form()

    async def register(e):
        try:
            refresh_form()
            if submit_button.disabled:
                show_error(page, "Username, organization, email, password, confirm password, and permit are required.")
                return

            response = await asyncio.to_thread(
                AuthService.register_ngo,
                username=username.value,
                email=email.value,
                password=password.value,
                organization_name=organization_name.value,
                permit_file_path=selected_permit_path["value"],
                registration_number=registration_number.value,
                phone=phone.value,
            )

            if response.status_code in (200, 201):
                show_success(page, "Registration successful. Verify OTP, then wait for admin approval.")
                AppState.pending_otp_email = email.value
                await page.push_route("/otp")
            else:
                try:
                    error_data = response.json()
                except ValueError:
                    error_data = {"detail": response.text}
                error_msg = error_data.get("detail") or _format_error_message(error_data)
                show_error(page, f"Registration failed: {error_msg}")
        except Exception as ex:
            show_error(page, f"Error: {str(ex)}")

    async def go_back(e):
        await page.push_route("/role-selection")

    username.on_change = refresh_form
    organization_name.on_change = refresh_form
    email.on_change = refresh_form
    password.on_change = refresh_form
    confirm_password.on_change = refresh_form
    submit_button.on_click = register
    submit_button.disabled = True

    permit_row = ft.Container(
        padding=16,
        border_radius=16,
        bgcolor="#FFFFFF",
        border=ft.Border.all(1, "#D6E2D3"),
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.UPLOAD_FILE, color="#6A994E"),
                        ft.Text("NGO Permit", size=16, weight=ft.FontWeight.BOLD, color="#1F2937"),
                    ],
                    spacing=10,
                ),
                muted_text("Upload the permit document that admin will review before activating the NGO account."),
                ft.Row(
                    [
                        secondary_button("Choose Permit", pick_permit, width=170, icon=ft.Icons.ATTACH_FILE),
                        permit_file_label,
                    ],
                    wrap=True,
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                #status_chip("Required for NGO registration", color="#073D1C"),
            ],
            spacing=12,
        ),
    )

    card = form_container(
        "Register as NGO",
        [
            muted_text("Create an NGO account, upload your permit, verify OTP, and wait for admin approval."),
            _field_block(username, username_error),
            _field_block(organization_name, organization_name_error),
            _field_block(email, email_error),
            registration_number,
            phone,
            _field_block(password, password_error),
            _field_block(confirm_password, confirm_password_error),
            permit_row,
            permit_error,
            submit_button,
            ft.Row(
                [subtle_text_button("Back", go_back)],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
        subtitle="NGO accounts require permit approval before they can access the full app.",
    )

    refresh_form(update_page=False)
    return auth_scaffold(page, "/register/ngo", "NGO Registration", card)
