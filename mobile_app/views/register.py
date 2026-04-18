import asyncio
import flet as ft
from services.auth_service import AuthService
from utils.app_state import AppState
from utils.constants import PRIMARY_GREEN, SECONDARY_GREEN, BUTTON_TEXT, INPUT_TEXT
from utils.helpers import auth_scaffold, form_container, show_message


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
    """Donor registration screen"""
    username = ft.TextField(label="Username", color=INPUT_TEXT, prefix_icon=ft.Icons.PERSON)
    full_name = ft.TextField(label="Full Name", color=INPUT_TEXT, prefix_icon=ft.Icons.PERSON)
    email = ft.TextField(label="Email", color=INPUT_TEXT, prefix_icon=ft.Icons.EMAIL)
    phone = ft.TextField(label="Phone (Optional)", color=INPUT_TEXT, prefix_icon=ft.Icons.PHONE)
    password = ft.TextField(label="Password", color=INPUT_TEXT, password=True, prefix_icon=ft.Icons.LOCK)

    async def register(e):
        try:
            if not username.value or not full_name.value or not email.value or not password.value:
                show_message(page, "Please fill all required fields", "red")
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
                show_message(page, "Registration successful! Check email for OTP.", "green")
                AppState.pending_otp_email = email.value
                await page.push_route("/otp")
            else:
                try:
                    error_data = response.json()
                except ValueError:
                    error_data = {"detail": response.text}
                error_msg = error_data.get('detail') or _format_error_message(error_data)
                show_message(page, f"Registration failed: {error_msg}", "red")
        except Exception as ex:
            show_message(page, f"Error: {str(ex)}", "red")

    async def go_back(e):
        await page.push_route("/role-selection")

    card = form_container("Register as Donor", [
        ft.Text("Create a donor account to post donations and coordinate handoffs.", size=14, color="#4B5563"),
        username,
        full_name,
        email,
        phone,
        password,
        ft.Button("Register", on_click=register, bgcolor=PRIMARY_GREEN, color=BUTTON_TEXT, width=300, height=45),
        ft.TextButton(
            "Back",
            on_click=go_back,
            style=ft.ButtonStyle(color=SECONDARY_GREEN),
        ),
    ])

    return auth_scaffold(page, "/register/donor", "Donor Registration", card)


def register_ngo_view(page: ft.Page):
    """NGO registration screen"""
    username = ft.TextField(label="Username", color=INPUT_TEXT, prefix_icon=ft.Icons.PERSON)
    organization_name = ft.TextField(label="Organization Name", color=INPUT_TEXT, prefix_icon=ft.Icons.BUSINESS)
    email = ft.TextField(label="Email", color=INPUT_TEXT, prefix_icon=ft.Icons.EMAIL)
    registration_number = ft.TextField(label="Registration Number (Optional)", color=INPUT_TEXT)
    phone = ft.TextField(label="Phone (Optional)", color=INPUT_TEXT, prefix_icon=ft.Icons.PHONE)
    password = ft.TextField(label="Password", color=INPUT_TEXT, password=True, prefix_icon=ft.Icons.LOCK)
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
            if not username.value or not organization_name.value or not email.value or not password.value or not selected_permit_path["value"]:
                show_message(page, "Username, organization, email, password, and permit are required.", "red")
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
                show_message(page, "Registration successful. Verify OTP, then wait for admin approval.", "green")
                AppState.pending_otp_email = email.value
                await page.push_route("/otp")
            else:
                try:
                    error_data = response.json()
                except ValueError:
                    error_data = {"detail": response.text}
                error_msg = error_data.get('detail') or _format_error_message(error_data)
                show_message(page, f"Registration failed: {error_msg}", "red")
        except Exception as ex:
            show_message(page, f"Error: {str(ex)}", "red")

    async def go_back(e):
        await page.push_route("/role-selection")

    card = form_container("Register as NGO", [
        ft.Text("Create an NGO account and upload the permit that admin will review.", size=14, color="#4B5563"),
        username,
        organization_name,
        email,
        registration_number,
        phone,
        password,
        ft.Row(
            [
                ft.Button("Choose Permit", on_click=pick_permit, bgcolor=SECONDARY_GREEN, color=BUTTON_TEXT),
                permit_file_label,
            ],
            wrap=True,
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        ft.Button("Register", on_click=register, bgcolor=PRIMARY_GREEN, color=BUTTON_TEXT, width=300, height=45),
        ft.TextButton(
            "Back",
            on_click=go_back,
            style=ft.ButtonStyle(color=SECONDARY_GREEN),
        ),
    ])

    return auth_scaffold(page, "/register/ngo", "NGO Registration", card)
