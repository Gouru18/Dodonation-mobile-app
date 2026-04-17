import flet as ft
from utils.constants import PRIMARY_GREEN, SECONDARY_GREEN, BUTTON_TEXT


def dashboard_view(page: ft.Page):
    return ft.View(
        route="/dashboard",
        appbar=ft.AppBar(title=ft.Text("Donation App - Dashboard")),
        controls=[
            ft.Container(
                expand=True,
                padding=20,
                content=ft.Column(
                    [
                        ft.Text("Welcome to DoDonation", size=26, weight=ft.FontWeight.BOLD),
                        ft.ElevatedButton("Open Chatbot", on_click=lambda e: page.go("/chatbot"), bgcolor=SECONDARY_GREEN, color=BUTTON_TEXT),
                        ft.ElevatedButton("View Map", on_click=lambda e: page.go("/map"), bgcolor=PRIMARY_GREEN, color=BUTTON_TEXT),
                        ft.ElevatedButton("Logout", on_click=lambda e: page.go("/"), bgcolor="#666", color=BUTTON_TEXT),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20,
                ),
            )
        ],
    )
