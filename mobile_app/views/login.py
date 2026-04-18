import flet as ft
from services.auth_service import AuthService
from utils.constants import PRIMARY_GREEN, SECONDARY_GREEN, BUTTON_TEXT, INPUT_TEXT
from utils.helpers import form_container, show_message


def login_view(page: ft.Page):
    email = ft.TextField(label="Email", color=INPUT_TEXT, prefix_icon=ft.Icons.EMAIL)
    password = ft.TextField(label="Password", color=INPUT_TEXT, password=True, prefix_icon=ft.Icons.LOCK)

    async def login(e):
        try:
            if not email.value or not password.value:
                show_message(page, "Please enter email and password", "red")
                return
            
            response = AuthService.login(email.value, password.value)
            if response.status_code == 200:
                data = response.json()
                AuthService.set_token(data.get("access"))
                AuthService.set_user(data.get("user", {}))
                show_message(page, "Login successful", "green")
                await page.push_route("/dashboard")
            else:
                error_data = response.json()
                error_msg = error_data.get('detail', 'Invalid credentials')
                show_message(page, error_msg, "red")
        except Exception as ex:
            show_message(page, f"Error: {str(ex)}", "red")

    async def go_to_register(e):
        await page.push_route("/role-selection")

    card = form_container("Login", [
        email,
        password,
        ft.Button(
            "Login",
            on_click=login,
            width=300,
            height=45,
            style=ft.ButtonStyle(
                bgcolor=PRIMARY_GREEN,
                color=BUTTON_TEXT
            )
        ),
        ft.Row(
            [
                ft.Text("If you don't have an account:", size=14, color="#666666"),
                ft.TextButton(
                    "Register",
                    on_click=go_to_register,
                    style=ft.ButtonStyle(
                        color=SECONDARY_GREEN
                    )
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=6,
        )
    ])
    
    return ft.View(
        route="/",
        appbar=ft.AppBar(title=ft.Text("Donation App - Login")),
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
