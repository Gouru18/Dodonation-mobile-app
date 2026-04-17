# pylint: disable=E1121, E1123
import flet as ft
from helpers import clear_page
from config import PRIMARY_GREEN, SECONDARY_GREEN, BUTTON_TEXT

def dashboard_screen(page, logout):
    clear_page(page)

    page.add(
        ft.Column(
            controls=[
                ft.Text("Dashboard", size=28, weight="bold"),
                ft.Container(
                    content=ft.Text("Welcome to DoDonation"),
                    padding=20,
                    bgcolor="white",
                    border_radius=10
                ),
                ft.Button("Logout", color=BUTTON_TEXT,bgcolor=PRIMARY_GREEN, on_click=lambda e: logout())
            ],
            spacing=20
        )
    )