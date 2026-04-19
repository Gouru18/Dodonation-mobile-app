import asyncio
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


def register_donor_view(page: ft.Page):
    username = auth_input("Username", ft.Icons.PERSON)
    full_name = auth_input("Full Name", ft.Icons.BADGE)
    email = auth_input("Email", ft.Icons.EMAIL)
    phone = auth_input("Phone (Optional)", ft.Icons.PHONE)
    password = auth_input("Password", ft.Icons.LOCK, password=True)

    async def register(e):
        try:
            if not username.value or not full_name.value or not email.value or not password.value:
                show_error(page, "Please fill all required fields")
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

    card = form_container(
        "Register as Donor",
        [
            muted_text("Create a donor account to post donations and manage handoff coordination."),
            username,
            full_name,
            email,
            phone,
            password,
            primary_button("Create Donor Account", register),
            ft.Row(
                [subtle_text_button("Back", go_back)],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
        subtitle="Donors can create donations, accept claims, and schedule meetings.",
    )

    return auth_scaffold(page, "/register/donor", "Donor Registration", card)


def register_ngo_view(page: ft.Page):
    username = auth_input("Username", ft.Icons.PERSON)
    organization_name = auth_input("Organization Name", ft.Icons.BUSINESS)
    email = auth_input("Email", ft.Icons.EMAIL)
    registration_number = auth_input("Registration Number (Optional)", ft.Icons.NUMBERS)
    phone = auth_input("Phone (Optional)", ft.Icons.PHONE)
    password = auth_input("Password", ft.Icons.LOCK, password=True)

    permit_file_label = ft.Text("No permit selected", color="#6B7280")
    selected_permit_path = {"value": None}

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
        page.update()

    async def register(e):
        try:
            if (
                not username.value
                or not organization_name.value
                or not email.value
                or not password.value
                or not selected_permit_path["value"]
            ):
                show_error(page, "Username, organization, email, password, and permit are required.")
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
                status_chip("Required for NGO registration", color="#B54708"),
            ],
            spacing=12,
        ),
    )

    card = form_container(
        "Register as NGO",
        [
            muted_text("Create an NGO account, upload your permit, verify OTP, and wait for admin approval."),
            username,
            organization_name,
            email,
            registration_number,
            phone,
            password,
            permit_row,
            primary_button("Create NGO Account", register),
            ft.Row(
                [subtle_text_button("Back", go_back)],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
        subtitle="NGO accounts require permit approval before they can access the full app.",
    )

    return auth_scaffold(page, "/register/ngo", "NGO Registration", card)