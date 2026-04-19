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


def otp_view(page: ft.Page):
    email = auth_input("Email", ft.Icons.EMAIL)
    email.value = AppState.pending_otp_email or ""
    email.read_only = True

    otp_code = auth_input("OTP Code", ft.Icons.PIN)

    async def load_pending_email():
        if not email.value:
            stored_email = await AuthService.get_pending_otp_email(page)
            if stored_email:
                AppState.pending_otp_email = stored_email
                email.value = stored_email
                page.update()

    page.run_task(load_pending_email)

    def _extract_error_message(error_data):
        if isinstance(error_data, dict):
            if "message" in error_data:
                return str(error_data["message"])
            if "detail" in error_data:
                return str(error_data["detail"])
            if "error" in error_data:
                return str(error_data["error"])
            if "non_field_errors" in error_data and error_data["non_field_errors"]:
                return str(error_data["non_field_errors"][0])
        return "Invalid OTP"

    async def verify_otp(e):
        try:
            if not email.value or not otp_code.value:
                show_error(page, "Please enter the OTP code")
                return

            response = await asyncio.to_thread(
                AuthService.verify_otp,
                email.value,
                otp_code.value
            )

            if response.status_code == 200:
                data = response.json()

                if data.get("requires_admin_approval"):
                    await AuthService.clear_pending_otp_email(page)
                    AppState.pending_otp_email = None
                    AuthService.logout()
                    show_success(
                        page,
                        data.get(
                            "message",
                            "OTP verified successfully. Your NGO account is now pending admin approval."
                        ),
                    )
                    await page.push_route("/")
                else:
                    AuthService.set_user(data.get("user", {}))
                    AuthService.set_token(data.get("access"))
                    await AuthService.persist_session(page)
                    await AuthService.clear_pending_otp_email(page)
                    AppState.pending_otp_email = None

                    show_success(page, "OTP verified successfully. You can now use the app.")
                    await page.push_route("/dashboard")
            else:
                try:
                    error_data = response.json()
                except ValueError:
                    error_data = {"error": response.text or "Invalid OTP"}

                show_error(page, _extract_error_message(error_data))

        except Exception as ex:
            show_error(page, f"Error: {str(ex)}")

    async def request_new_otp(e):
        try:
            if not email.value:
                show_error(page, "Missing email address")
                return

            response = await asyncio.to_thread(AuthService.request_otp, email.value)

            if response.status_code == 200:
                await AuthService.set_pending_otp_email(page, email.value)
                show_success(page, "A new OTP has been sent.")
            else:
                try:
                    error_data = response.json()
                except ValueError:
                    error_data = {"detail": response.text or "Failed to send OTP"}
                show_error(page, _extract_error_message(error_data))

        except Exception as ex:
            show_error(page, f"Error: {str(ex)}")

    async def go_back_to_login(e):
        await page.push_route("/")

    card = form_container(
        "Verify OTP",
        [
            muted_text("Enter the OTP linked to your registration email."),
            status_chip("Donor: access after OTP verification", color="#027A48"),
            status_chip("NGO: access only after admin reviews the permit", color="#B54708"),
            email,
            otp_code,
            primary_button("Verify OTP", verify_otp),
            secondary_button("Request New OTP", request_new_otp),
            ft.Row(
                [subtle_text_button("Back to Login", go_back_to_login)],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
        subtitle="Complete verification to continue.",
    )

    return auth_scaffold(page, "/otp", "OTP Verification", card)