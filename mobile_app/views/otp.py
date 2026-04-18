import asyncio
import flet as ft
from services.auth_service import AuthService
from utils.app_state import AppState
from utils.constants import PRIMARY_GREEN, SECONDARY_GREEN, BUTTON_TEXT, INPUT_TEXT
from utils.helpers import auth_scaffold, form_container, show_message


def otp_view(page: ft.Page):
    """OTP verification screen"""
    email = ft.TextField(
        label="Email",
        value=AppState.pending_otp_email,
        color=INPUT_TEXT,
        prefix_icon=ft.Icons.EMAIL,
        read_only=True,
    )
    otp_code = ft.TextField(label="OTP Code", color=INPUT_TEXT, prefix_icon=ft.Icons.CONFIRMATION_NUM)

    async def verify_otp(e):
        try:
            if not email.value or not otp_code.value:
                show_message(page, "Please enter email and OTP code", "red")
                return
            
            response = await asyncio.to_thread(AuthService.verify_otp, email.value, otp_code.value)
            if response.status_code == 200:
                data = response.json()
                if data.get("requires_admin_approval"):
                    AuthService.logout()
                    show_message(page, data.get("message", "Account pending admin approval."), "green")
                    await page.push_route("/")
                else:
                    AuthService.set_user(data.get("user", {}))
                    AuthService.set_token(data.get("access"))
                    show_message(page, "OTP verified successfully!", "green")
                    await page.push_route("/dashboard")
            else:
                error_data = response.json()
                error_msg = error_data.get('error', 'Invalid OTP')
                show_message(page, error_msg, "red")
        except Exception as ex:
            show_message(page, f"Error: {str(ex)}", "red")

    async def request_new_otp(e):
        try:
            if not email.value:
                show_message(page, "Please enter your email", "red")
                return
            
            response = await asyncio.to_thread(AuthService.request_otp, email.value)
            if response.status_code == 200:
                show_message(page, "New OTP sent to your email", "green")
            else:
                show_message(page, "Failed to send OTP", "red")
        except Exception as ex:
            show_message(page, f"Error: {str(ex)}", "red")

    async def go_back_to_login(e):
        await page.push_route("/")

    card = form_container("Verify OTP", [
        ft.Text("Enter the OTP sent to your registered email address.", size=14, color="#4B5563"),
        email,
        otp_code,
        ft.Button(
            "Verify OTP",
            on_click=verify_otp,
            bgcolor=PRIMARY_GREEN,
            color=BUTTON_TEXT,
            width=300,
            height=45
        ),
        ft.TextButton(
            "Request New OTP",
            on_click=request_new_otp,
            style=ft.ButtonStyle(color=SECONDARY_GREEN),
        ),
        ft.Divider(),
        ft.TextButton(
            "Back to Login",
            on_click=go_back_to_login,
            style=ft.ButtonStyle(color=SECONDARY_GREEN),
        ),
    ])

    return auth_scaffold(page, "/otp", "OTP Verification", card)
