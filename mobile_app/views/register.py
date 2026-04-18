import flet as ft
from services.auth_service import AuthService
from utils.app_state import AppState
from utils.constants import PRIMARY_GREEN, SECONDARY_GREEN, BUTTON_TEXT, INPUT_TEXT
from utils.helpers import form_container, show_message


def register_donor_view(page: ft.Page):
    """Donor registration screen"""
    full_name = ft.TextField(label="Full Name", color=INPUT_TEXT, prefix_icon=ft.Icons.PERSON)
    email = ft.TextField(label="Email", color=INPUT_TEXT, prefix_icon=ft.Icons.EMAIL)
    phone = ft.TextField(label="Phone (Optional)", color=INPUT_TEXT, prefix_icon=ft.Icons.PHONE)
    password = ft.TextField(label="Password", color=INPUT_TEXT, password=True, prefix_icon=ft.Icons.LOCK)

    async def register(e):
        try:
            if not full_name.value or not email.value or not password.value:
                show_message(page, "Please fill all required fields", "red")
                return
            
            response = AuthService.register_donor(
                email=email.value,
                password=password.value,
                full_name=full_name.value,
                phone=phone.value
            )
            
            if response.status_code in (200, 201):
                show_message(page, "Registration successful! Check email for OTP.", "green")
                AppState.pending_otp_email = email.value
                await page.push_route("/otp")
            else:
                error_data = response.json()
                error_msg = error_data.get('detail') or str(error_data)
                show_message(page, f"Registration failed: {error_msg}", "red")
        except Exception as ex:
            show_message(page, f"Error: {str(ex)}", "red")

    async def go_back(e):
        await page.push_route("/role-selection")

    card = form_container("Register as Donor", [
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

    return ft.View(
        route="/register/donor",
        appbar=ft.AppBar(title=ft.Text("Donation App - Donor Registration")),
        controls=[
            ft.Container(
                expand=True,
                padding=20,
                alignment=ft.Alignment.CENTER,
                content=ft.Column(
                    [card],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            )
        ],
    )


def register_ngo_view(page: ft.Page):
    """NGO registration screen"""
    organization_name = ft.TextField(label="Organization Name", color=INPUT_TEXT, prefix_icon=ft.Icons.BUSINESS)
    email = ft.TextField(label="Email", color=INPUT_TEXT, prefix_icon=ft.Icons.EMAIL)
    registration_number = ft.TextField(label="Registration Number (Optional)", color=INPUT_TEXT)
    phone = ft.TextField(label="Phone (Optional)", color=INPUT_TEXT, prefix_icon=ft.Icons.PHONE)
    password = ft.TextField(label="Password", color=INPUT_TEXT, password=True, prefix_icon=ft.Icons.LOCK)

    async def register(e):
        try:
            if not organization_name.value or not email.value or not password.value:
                show_message(page, "Please fill all required fields", "red")
                return
            
            response = AuthService.register_ngo(
                email=email.value,
                password=password.value,
                organization_name=organization_name.value,
                registration_number=registration_number.value,
                phone=phone.value
            )
            
            if response.status_code in (200, 201):
                show_message(page, "Registration successful! Check email for OTP.", "green")
                AppState.pending_otp_email = email.value
                await page.push_route("/otp")
            else:
                error_data = response.json()
                error_msg = error_data.get('detail') or str(error_data)
                show_message(page, f"Registration failed: {error_msg}", "red")
        except Exception as ex:
            show_message(page, f"Error: {str(ex)}", "red")

    async def go_back(e):
        await page.push_route("/role-selection")

    card = form_container("Register as NGO", [
        organization_name,
        email,
        registration_number,
        phone,
        password,
        ft.Button("Register", on_click=register, bgcolor=PRIMARY_GREEN, color=BUTTON_TEXT, width=300, height=45),
        ft.TextButton(
            "Back",
            on_click=go_back,
            style=ft.ButtonStyle(color=SECONDARY_GREEN),
        ),
    ])

    return ft.View(
        route="/register/ngo",
        appbar=ft.AppBar(title=ft.Text("Donation App - NGO Registration")),
        controls=[
            ft.Container(
                expand=True,
                padding=20,
                alignment=ft.Alignment.CENTER,
                content=ft.Column(
                    [card],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            )
        ],
    )
