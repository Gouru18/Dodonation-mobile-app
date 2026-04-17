# pylint: disable=E1121, E1123
import flet as ft
from archive.dodonation_app.helpers import clear_page
from archive.dodonation_app.config import PRIMARY_GREEN, SECONDARY_GREEN, BUTTON_TEXT

def dashboard_screen(page, logout, go_to_chatbot=None):
    clear_page(page)

    controls = [
        ft.Text("Dashboard", size=28, weight="bold"),
        ft.Container(
            content=ft.Text("Welcome to DoDonation"),
            padding=20,
            bgcolor="white",
            border_radius=10
        ),
        ft.Button("Logout", color=BUTTON_TEXT,bgcolor=PRIMARY_GREEN, on_click=lambda e: logout())
    ]

    if go_to_chatbot:
        controls.insert(2, ft.Button("Chat with Bot", color=BUTTON_TEXT, bgcolor=SECONDARY_GREEN, on_click=lambda e: go_to_chatbot()))

    page.add(
        ft.Column(
            controls=controls,
            spacing=20
        )
    )