# pylint: disable=E1121, E1123
import flet as ft
from archive.dodonation_app.auth_api import register_user
from archive.dodonation_app.helpers import show_message, clear_page, form_container
from archive.dodonation_app.config import PRIMARY_GREEN, SECONDARY_GREEN, BUTTON_TEXT, INPUT_TEXT

def register_screen(page, role, go_to_otp, go_back, set_email):
    clear_page(page)

    name = ft.TextField(label="Name", color= INPUT_TEXT, prefix_icon=ft.Icons.PERSON)
    email = ft.TextField(label="Email", color= INPUT_TEXT, prefix_icon=ft.Icons.EMAIL)
    password = ft.TextField(label="Password", color= INPUT_TEXT, password=True, prefix_icon=ft.Icons.LOCK)

    def register(e):
        try:
            res = register_user(name.value, email.value, password.value, role)

            if res.status_code == 201:
                set_email(email.value)
                show_message(page, "OTP sent")
                go_to_otp()
            else:
                show_message(page, "Registration failed", "red")

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