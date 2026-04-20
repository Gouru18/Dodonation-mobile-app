import flet as ft

from dodonation_app.screens.login import login_screen
from dodonation_app.screens.register import register_screen
from dodonation_app.screens.role_selection import role_selection_screen
from dodonation_app.screens.otp import otp_screen
from dodonation_app.screens.dashboard import dashboard_screen

def main(page: ft.Page):

    page.bgcolor = "#f5f6fa"
    page.padding = 20
    page.title = "DoDonation App"
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"

    # STATE
    selected_role = None
    temp_email = None

    # STATE SETTERS
    def set_role(role):
        nonlocal selected_role
        selected_role = role

    def set_email(email):
        nonlocal temp_email
        temp_email = email

    # NAVIGATION
    def go_to_login():
        login_screen(page, go_to_role_selection, go_to_dashboard)

    def go_to_role_selection():
        role_selection_screen(page, set_role, go_to_register, go_to_login)

    def go_to_register():
        register_screen(page, selected_role, go_to_otp, go_to_role_selection, set_email)

    def go_to_otp():
        otp_screen(page, temp_email, go_to_login)

    def go_to_dashboard():
        dashboard_screen(page, go_to_login)

    # START
    go_to_login()


ft.app(target=main)
