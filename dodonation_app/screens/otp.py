# pylint: disable=E1121, E1123
import flet as ft
from auth_api import verify_otp
from helpers import show_message, clear_page
from config import PRIMARY_GREEN, SECONDARY_GREEN, BUTTON_TEXT


def otp_screen(page, email, go_to_login):
    clear_page(page)

    otp = ft.TextField(label="Enter OTP", text_align="center")

    def verify(e):
        try:
            res = verify_otp(email, otp.value)

            if res.status_code == 200:
                show_message(page, "Verified")
                go_to_login()
            else:
                show_message(page, "Invalid OTP", "red")

        except Exception as ex:
            print(ex)
            show_message(page, "Server error", "red")

    card = form_container("OTP Verification", [
        otp,
        ft.Button("Verify", color=BUTTON_TEXT,bgcolor=PRIMARY_GREEN, width=300, on_click=verify),
        ft.TextButton("Back to Login", 
                      style=ft.ButtonStyle(
                      color=SECONDARY_GREEN
                      ), 
                      on_click=lambda e: go_to_login())
    ])

    page.add(
        ft.Column(
            controls=[card],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )