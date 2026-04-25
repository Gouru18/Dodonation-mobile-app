import flet as ft

from services.auth_service import AuthService
from services.profile_service import ProfileService
from services.permit_service import PermitService
from utils.helpers import (
    build_appbar,
    centered_content,
    page_container,
    section_card,
    auth_input,
    primary_button,
    secondary_button,
    muted_text,
    status_chip,
    show_error,
    show_success,
)


def _inline_error():
    return ft.Text("", color="#B42318", size=12, visible=False)


def _field_block(field, error_label):
    return ft.Column([field, error_label], spacing=4)


def _set_inline_error(field, error_label, message):
    field.error_text = message
    error_label.value = message or ""
    error_label.visible = bool(message)


def _validate_phone(value):
    raw = (value or "").strip()
    if not raw:
        return None

    allowed = set("0123456789+ -()")
    if any(char not in allowed for char in raw):
        return "Phone number can contain digits, spaces, +, -, and parentheses only."

    if sum(char.isdigit() for char in raw) < 7:
        return "Enter a valid phone number with at least 7 digits."

    return None


def profile_view(page: ft.Page):
    user = AuthService.user or {}
    is_donor = user.get("role") == "donor"

    full_name = auth_input("Full Name", ft.Icons.PERSON)
    organization_name = auth_input("Organization Name", ft.Icons.BUSINESS)
    registration_number = auth_input("Registration Number", ft.Icons.BADGE)
    phone = auth_input("Phone Number", ft.Icons.PHONE)
    phone_error = _inline_error()
    address = auth_input("Address", ft.Icons.LOCATION_ON, multiline=True)
    address.min_lines = 3

    info_message = ft.Text("", color="#4B5563")
    role_chip = status_chip(
        f"Role: {'Donor' if is_donor else 'NGO'}",
        color="#1D4ED8",
    )

    def refresh_form(*_, update_page=True):
        phone_message = _validate_phone(phone.value)
        _set_inline_error(phone, phone_error, phone_message)
        if update_page:
            page.update()

    async def persist_user_state():
        await AuthService.persist_session(page)

    def load_profile():
        response = (
            ProfileService.get_donor_profile()
            if is_donor
            else ProfileService.get_ngo_profile()
        )

        if response.status_code != 200:
            info_message.value = f"Could not load profile: {response.text}"
            page.update()
            return

        data = response.json()

        if is_donor:
            full_name.value = data.get("full_name", "")
            info_message.value = "Update your donor contact details below."
        else:
            organization_name.value = data.get("organization_name", "")
            registration_number.value = data.get("registration_number", "")

            permit = data.get("permit_application")
            if permit:
                permit_status = PermitService.display_status(
                    permit.get("status", "unknown")
                )
                info_message.value = f"Permit status: {permit_status}"
            else:
                info_message.value = "Permit not uploaded yet."

        phone.value = (
            data.get("phone", "")
            or (data.get("user") or {}).get("phone", "")
            or user.get("phone", "")
        )
        address.value = data.get("address", "")
        refresh_form(update_page=False)
        page.update()

    def save_profile(e):
        phone_message = _validate_phone(phone.value)
        _set_inline_error(phone, phone_error, phone_message)
        page.update()

        if phone_message:
            show_error(page, "Please fix the highlighted phone number field.")
            return

        if is_donor:
            response = ProfileService.update_donor_profile(
                full_name=full_name.value,
                address=address.value,
                phone=phone.value.strip(),
            )
        else:
            response = ProfileService.update_ngo_profile(
                organization_name=organization_name.value,
                registration_number=registration_number.value,
                address=address.value,
                phone=phone.value.strip(),
            )

        if response.status_code == 200:
            if AuthService.user is not None:
                AuthService.user["phone"] = phone.value.strip()
                page.run_task(persist_user_state)
            show_success(page, "Profile updated.")
            load_profile()
        else:
            show_error(page, f"Could not update profile: {response.text}")

    async def go_back(e):
        await page.push_route("/dashboard")

    load_profile()

    profile_controls = [
        ft.Row(
            [
                role_chip,
            ],
            wrap=True,
            spacing=10,
        ),
        muted_text(f"Signed in as: {user.get('email', 'No email')}"),
        info_message,
    ]

    if is_donor:
        profile_controls.append(full_name)
    else:
        profile_controls.extend([organization_name, registration_number])

    profile_controls.extend(
        [
            _field_block(phone, phone_error),
            address,
            ft.Row(
                [
                    primary_button(
                        "Save Profile",
                        save_profile,
                        width=170,
                        icon=ft.Icons.SAVE,
                    ),
                    secondary_button(
                        "Back",
                        go_back,
                        width=140,
                        icon=ft.Icons.ARROW_BACK,
                    ),
                ],
                spacing=12,
                wrap=True,
            ),
        ]
    )

    phone.on_change = refresh_form
    return ft.View(
        route="/profile",
        appbar=build_appbar("My Profile", go_back),
        controls=[
            page_container(
                centered_content(
                    section_card(
                        "Profile Details",
                        profile_controls,
                        subtitle="Keep your contact details and pickup information up to date.",
                    ),
                    max_width=760,
                )
            )
        ],
    )
