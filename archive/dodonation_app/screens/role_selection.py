# pylint: disable=E1121, E1123
import flet as ft
from archive.dodonation_app.helpers import clear_page, form_container
from archive.dodonation_app.config import PRIMARY_GREEN, SECONDARY_GREEN, BUTTON_TEXT

def role_selection_screen(page, set_role, go_to_register, go_back):
    clear_page(page)

    def select(role):
        set_role(role)
        go_to_register()

    card = form_container("Select Role", [
        ft.Button("Donor",color=BUTTON_TEXT,bgcolor=PRIMARY_GREEN, width=300, on_click=lambda e: select("donor")),
        ft.Button("NGO", color=BUTTON_TEXT,bgcolor=PRIMARY_GREEN, width=300, on_click=lambda e: select("ngo")),
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