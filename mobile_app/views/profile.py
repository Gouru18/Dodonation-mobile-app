import flet as ft

from services.auth_service import AuthService
from services.profile_service import ProfileService
from utils.constants import PRIMARY_GREEN, BUTTON_TEXT, INPUT_TEXT
from utils.helpers import show_message


def profile_view(page: ft.Page):
    is_donor = AuthService.user and AuthService.user.get("role") == "donor"

    full_name = ft.TextField(label="Full Name", color=INPUT_TEXT)
    organization_name = ft.TextField(label="Organization Name", color=INPUT_TEXT)
    registration_number = ft.TextField(label="Registration Number", color=INPUT_TEXT)
    address = ft.TextField(label="Address", multiline=True, min_lines=3, color=INPUT_TEXT)
    info_text = ft.Text("")

    def load_profile():
        response = ProfileService.get_donor_profile() if is_donor else ProfileService.get_ngo_profile()
        if response.status_code != 200:
            info_text.value = f"Could not load profile: {response.text}"
            page.update()
            return

        data = response.json()
        if is_donor:
            full_name.value = data.get("full_name", "")
        else:
            organization_name.value = data.get("organization_name", "")
            registration_number.value = data.get("registration_number", "")
            permit = data.get("permit_application")
            if permit:
                info_text.value = f"Permit status: {permit.get('status', 'unknown')}"
            else:
                info_text.value = "Permit not uploaded yet."
        address.value = data.get("address", "")
        page.update()

    def save_profile(e):
        if is_donor:
            response = ProfileService.update_donor_profile(full_name=full_name.value, address=address.value)
        else:
            response = ProfileService.update_ngo_profile(
                organization_name=organization_name.value,
                registration_number=registration_number.value,
                address=address.value,
            )

        if response.status_code == 200:
            show_message(page, "Profile updated.", "green")
            load_profile()
        else:
            show_message(page, f"Could not update profile: {response.text}", "red")

    async def go_back(e):
        await page.push_route("/dashboard")

    load_profile()

    controls = [info_text]
    if is_donor:
        controls.append(full_name)
    else:
        controls.extend([organization_name, registration_number])
    controls.extend(
        [
            address,
            ft.Button("Save Profile", on_click=save_profile, bgcolor=PRIMARY_GREEN, color=BUTTON_TEXT),
            ft.Button("Back", on_click=go_back, bgcolor="#666666", color=BUTTON_TEXT),
        ]
    )

    return ft.View(
        route="/profile",
        appbar=ft.AppBar(title=ft.Text("My Profile")),
        controls=[
            ft.Container(
                expand=True,
                padding=20,
                content=ft.Column(controls, spacing=15),
            )
        ],
    )
