# pylint: disable=E1121, E1123
import flet as ft
from helpers import form_container, show_message, clear_page
from auth_api import login_user
from config import PRIMARY_GREEN, SECONDARY_GREEN, BUTTON_TEXT, INPUT_TEXT


def login_screen(page, go_to_register, go_to_dashboard):
    clear_page(page)

    email = ft.TextField(label="Email", color=INPUT_TEXT, prefix_icon=ft.Icons.EMAIL)
    password = ft.TextField(label="Password", color=INPUT_TEXT, password=True, prefix_icon=ft.Icons.LOCK)

    def login(e):
        try:
            res = login_user(email.value, password.value)

            if res.status_code == 200:
                show_message(page, "Login successful")
                go_to_dashboard()
            else:
                show_message(page, "Invalid credentials", "red")

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