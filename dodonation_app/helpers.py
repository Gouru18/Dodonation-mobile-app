# pylint: disable=E1121, E1123
import flet as ft

import flet as ft

def form_container(title, controls):
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(title, size=24, weight="bold"),
                ft.Divider(),
                *controls
            ],
            spacing=15
        ),
        padding=20,
        width=350,
        bgcolor="white",
        border_radius=15,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=10,
            color="#cccccc"
        )
    )

def show_message(page, msg, color="green"):
    page.snack_bar = ft.SnackBar(
        ft.Text(msg),
        bgcolor=color
    )
    page.snack_bar.open = True
    page.update()


def clear_page(page):
    page.controls.clear()