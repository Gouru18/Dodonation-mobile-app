import flet as ft
from utils.constants import PRIMARY_GREEN, SECONDARY_GREEN, BUTTON_TEXT

def dashboard_view(page: ft.Page):
    async def open_chatbot(e):
        await page.push_route("/chatbot")

    async def view_map(e):
        await page.push_route("/map")

    async def logout(e):
        await page.push_route("/")

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
                        ft.Button("Open Chatbot", on_click=open_chatbot, bgcolor=SECONDARY_GREEN, color=BUTTON_TEXT),
                        ft.Button("View Map", on_click=view_map, bgcolor=PRIMARY_GREEN, color=BUTTON_TEXT),
                        ft.Button("Logout", on_click=logout, bgcolor="#666", color=BUTTON_TEXT),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20,
                ),
            )
        ],
    )
