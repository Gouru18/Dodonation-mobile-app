import asyncio
import os
from datetime import datetime, date, time
from urllib.parse import urljoin, urlparse
import flet as ft

from services.auth_service import AuthService
from services.donation_service import DonationService
from utils.config import BASE_URL
from utils.helpers import (
    build_appbar,
    page_container,
    centered_content,
    section_card,
    auth_input,
    primary_button,
    secondary_button,
    muted_text,
    status_chip,
    show_error,
    show_success,
)


CATEGORY_OPTIONS = [
    ft.dropdown.Option("food"),
    ft.dropdown.Option("clothing"),
    ft.dropdown.Option("medical"),
    ft.dropdown.Option("books"),
    ft.dropdown.Option("furniture"),
    ft.dropdown.Option("electronics"),
    ft.dropdown.Option("other"),
]

FILTER_CATEGORY_OPTIONS = [
    ft.dropdown.Option(key="all", text="All Categories"),
    ft.dropdown.Option(key="food", text="Food"),
    ft.dropdown.Option(key="clothing", text="Clothing"),
    ft.dropdown.Option(key="medical", text="Medical"),
    ft.dropdown.Option(key="books", text="Books"),
    ft.dropdown.Option(key="furniture", text="Furniture"),
    ft.dropdown.Option(key="electronics", text="Electronics"),
    ft.dropdown.Option(key="other", text="Other"),
]

FILTER_STATUS_OPTIONS = [
    ft.dropdown.Option(key="all", text="All Statuses"),
    ft.dropdown.Option(key="available", text="Available"),
    ft.dropdown.Option(key="pending", text="Pending"),
]


def _inline_error():
    return ft.Text("", color="#B42318", size=12, visible=False)


def _field_block(field, error_label):
    return ft.Column([field, error_label], spacing=4)


def _set_inline_error(field, error_label, message):
    field.error_text = message
    error_label.value = message or ""
    error_label.visible = bool(message)


def _validate_quantity(value):
    raw = (value or "").strip()
    if not raw:
        return "Quantity is required."
    if not raw.isdigit():
        return "Quantity must contain numbers only."
    if int(raw) <= 0:
        return "Quantity must be greater than zero."
    return None


def _validate_donation_date(value):
    raw = (value or "").strip()
    if not raw:
        return None
    try:
        parsed_date = datetime.strptime(raw, "%Y-%m-%d").date()
    except ValueError:
        return "Use a valid date in YYYY-MM-DD format."
    if parsed_date < date.today():
        return "Expiry date cannot be in the past."
    return None


def _parse_picker_date(value):
    if isinstance(value, datetime):
        return value

    raw = str(value or "").strip()
    if not raw:
        return None

    try:
        return datetime.strptime(raw, "%Y-%m-%d")
    except ValueError:
        return None


def _format_picker_date(value):
    parsed_date = _parse_picker_date(value)
    if not parsed_date:
        return ""
    return parsed_date.strftime("%Y-%m-%d")


def donations_view(page: ft.Page):
    is_donor = AuthService.user and AuthService.user.get("role") == "donor"
    donations_column = ft.Column(spacing=12, scroll=ft.ScrollMode.AUTO)
    media_base_url = BASE_URL.rsplit("/api", 1)[0]
    image_fit_cover = getattr(getattr(ft, "ImageFit", None), "COVER", "cover")
    donor_edit_state = {}
    claim_notice_state = {"token": 0}
    selected_category_filter = {"value": "all"}
    selected_status_filter = {"value": "all"}
    claim_notice = ft.Container(
        visible=False,
        padding=16,
        border_radius=16,
        bgcolor="#ECFDF3",
        border=ft.Border.all(1, "#ABEFC6"),
    )
    category_filter = ft.Dropdown(
        label="Filter by Category",
        options=FILTER_CATEGORY_OPTIONS,
        value="all",
        border_radius=14,
        filled=True,
        bgcolor="white",
        width=220,
    )
    status_filter = ft.Dropdown(
        label="Filter by Status",
        options=FILTER_STATUS_OPTIONS,
        value="all",
        border_radius=14,
        filled=True,
        bgcolor="white",
        width=220,
    )

    def hide_claim_notice():
        claim_notice.visible = False
        claim_notice.content = None
        page.update()

    async def auto_hide_claim_notice(token):
        await asyncio.sleep(4)
        if claim_notice_state["token"] == token:
            hide_claim_notice()

    title = auth_input("Title", ft.Icons.TITLE)
    description = auth_input("Description", ft.Icons.DESCRIPTION, multiline=True)
    category = ft.Dropdown(
        label="Category",
        options=CATEGORY_OPTIONS,
        value="other",
        border_radius=14,
        filled=True,
        bgcolor="white",
    )
    quantity = auth_input("Quantity", ft.Icons.NUMBERS)
    quantity.value = "1"
    expiry_date = auth_input("Expiry Date", ft.Icons.CALENDAR_MONTH)
    expiry_date.width = 240
    expiry_date.read_only = True
    expiry_date.hint_text = "Pick an expiry date"
    title_error = _inline_error()
    description_error = _inline_error()
    quantity_error = _inline_error()
    expiry_date_error = _inline_error()

    selected_image = ft.Text("No image selected", color="#6B7280")
    selected_image_path = {"value": None}

    def refresh_create_form(*_, update_page=True):
        title_message = None if title.value and title.value.strip() else "Title is required."
        description_message = None if description.value and description.value.strip() else "Description is required."
        quantity_message = _validate_quantity(quantity.value)
        expiry_message = _validate_donation_date(expiry_date.value)
        _set_inline_error(title, title_error, title_message)
        _set_inline_error(description, description_error, description_message)
        _set_inline_error(quantity, quantity_error, quantity_message)
        _set_inline_error(expiry_date, expiry_date_error, expiry_message)
        if update_page:
            page.update()

    def set_create_expiry_date_value(selected_date, update_page=True):
        expiry_date.value = _format_picker_date(selected_date)
        refresh_create_form(update_page=update_page)

    def handle_create_date_change(e):
        set_create_expiry_date_value(e.control.value)

    create_expiry_date_picker = ft.DatePicker(
        modal=True,
        value=datetime.now(),
        first_date=datetime.combine(date.today(), time.min),
        last_date=datetime(date.today().year + 5, 12, 31),
        help_text="Select expiry date",
        confirm_text="Choose",
        cancel_text="Cancel",
        error_format_text="Pick a valid date.",
        error_invalid_text="Expiry date cannot be in the past.",
        entry_mode=ft.DatePickerEntryMode.CALENDAR_ONLY,
        on_change=handle_create_date_change,
    )

    def open_create_expiry_picker(e):
        selected_date = _parse_picker_date(expiry_date.value)
        create_expiry_date_picker.value = selected_date or datetime.combine(date.today(), time.min)
        page.show_dialog(create_expiry_date_picker)

    def clear_create_expiry_date(e):
        set_create_expiry_date_value("", update_page=True)

    def resolve_image_src(item):
        image_src = item.get("image_url") or item.get("image")
        if not image_src:
            return None

        parsed = urlparse(str(image_src))
        if parsed.scheme and parsed.netloc:
            return image_src

        return urljoin(f"{media_base_url}/", str(image_src).lstrip("/"))

    def display_status(status):
        normalized_status = (status or "available").strip().lower()
        if normalized_status == "pending":
            return "available"
        return normalized_status

    def donor_feed_status(item):
        normalized_status = (
            item.get("feed_status") or item.get("status") or "available"
        ).strip().lower()

        if normalized_status == "completed":
            return "claimed"

        if normalized_status == "expired":
            return "rejected"

        if normalized_status not in {"available", "pending", "claimed", "rejected"}:
            return "available"

        return normalized_status

    def current_feed_status(item):
        return donor_feed_status(item) if is_donor else display_status(item.get("status"))

    def filter_matches(item):
        category_value = selected_category_filter["value"]
        status_value = selected_status_filter["value"]
        item_category = (item.get("category") or "").strip().lower()
        item_status = current_feed_status(item)

        matches_category = category_value == "all" or item_category == category_value

        if status_value == "all":
            matches_status = True
        elif not is_donor and status_value == "pending":
            matches_status = item_status == "available"
        else:
            matches_status = item_status == status_value

        return matches_category and matches_status

    def no_results_message():
        parts = []
        if selected_category_filter["value"] != "all":
            parts.append(f"category '{selected_category_filter['value']}'")
        if selected_status_filter["value"] != "all":
            parts.append(f"status '{selected_status_filter['value']}'")

        if parts:
            return f"There are no donations for the selected {' and '.join(parts)} filter."
        return "No donations found yet."

    def status_color(status):
        return {
            "available": "#027A48",
            "pending": "#B54708",
            "claimed": "#1D4ED8",
            "expired": "#B54708",
            "rejected": "#B42318",
        }.get(status, "#667085")

    def get_donor_edit_state(item):
        donation_id = item["id"]
        state = donor_edit_state.get(donation_id)
        if state is None:
            state = {
                "is_editing": False,
                "title": item.get("title", ""),
                "description": item.get("description", ""),
                "category": item.get("category", "other"),
                "quantity": str(item.get("quantity", 1)),
                "expiry_date": item.get("expiry_date") or "",
                "image_path": None,
                "image_label": "Keep current image",
                "confirming_delete": False,
            }
            donor_edit_state[donation_id] = state
        return state

    def reset_donor_edit_state(item):
        donation_id = item["id"]
        donor_edit_state[donation_id] = {
            "is_editing": False,
            "title": item.get("title", ""),
            "description": item.get("description", ""),
            "category": item.get("category", "other"),
            "quantity": str(item.get("quantity", 1)),
            "expiry_date": item.get("expiry_date") or "",
            "image_path": None,
            "image_label": "Keep current image",
            "confirming_delete": False,
        }

    def donation_card(item):
        donor_data = item.get("donor") or {}
        status = current_feed_status(item)
        image_src = resolve_image_src(item)
        edit_state = get_donor_edit_state(item)

        controls = [
            ft.Text(
                item.get("title", "Untitled"),
                size=18,
                weight=ft.FontWeight.BOLD,
                color="#1F2937",
            ),
            muted_text(item.get("description", "")),
        ]

        if image_src:
            controls.append(
                ft.Container(
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    border_radius=16,
                    content=ft.Image(
                        src=image_src,
                        width=520,
                        height=220,
                        fit=image_fit_cover,
                        error_content=ft.Container(
                            padding=16,
                            bgcolor="#F2F4F7",
                            content=muted_text("Image could not be loaded."),
                        ),
                    ),
                )
            )

        controls.extend(
            [
                ft.Row(
                    [
                        status_chip(f"Category: {item.get('category', 'n/a')}", color="#1D4ED8"),
                        status_chip(f"Qty: {item.get('quantity', 1)}", color="#027A48"),
                        status_chip(f"Status: {status}", color=status_color(status)),
                    ],
                    wrap=True,
                    spacing=8,
                ),
                muted_text(f"Donor: {donor_data.get('email', 'Unknown')}"),
            ]
        )

        if is_donor:
            title_field = auth_input("Title", ft.Icons.TITLE)
            title_field.value = edit_state["title"]
            description_field = auth_input("Description", ft.Icons.DESCRIPTION, multiline=True)
            description_field.value = edit_state["description"]
            category_field = ft.Dropdown(
                label="Category",
                options=CATEGORY_OPTIONS,
                value=edit_state["category"],
                border_radius=14,
                filled=True,
                bgcolor="white",
            )
            quantity_field = auth_input("Quantity", ft.Icons.NUMBERS)
            quantity_field.value = edit_state["quantity"]
            expiry_field = auth_input("Expiry Date", ft.Icons.CALENDAR_MONTH)
            expiry_field.width = 240
            expiry_field.value = edit_state["expiry_date"]
            expiry_field.read_only = True
            expiry_field.hint_text = "Pick an expiry date"
            quantity_field_error = _inline_error()
            expiry_field_error = _inline_error()
            edit_image_label = ft.Text(edit_state["image_label"], color="#6B7280")

            def refresh_edit_form(*_, update_page=True):
                quantity_message = _validate_quantity(quantity_field.value)
                expiry_message = _validate_donation_date(expiry_field.value)
                _set_inline_error(quantity_field, quantity_field_error, quantity_message)
                _set_inline_error(expiry_field, expiry_field_error, expiry_message)
                if update_page:
                    page.update()

            def set_edit_expiry_date_value(selected_date, update_page=True):
                expiry_field.value = _format_picker_date(selected_date)
                refresh_edit_form(update_page=update_page)

            def handle_edit_date_change(e):
                set_edit_expiry_date_value(e.control.value)

            edit_expiry_date_picker = ft.DatePicker(
                modal=True,
                value=datetime.now(),
                first_date=datetime.combine(date.today(), time.min),
                last_date=datetime(date.today().year + 5, 12, 31),
                help_text="Select expiry date",
                confirm_text="Choose",
                cancel_text="Cancel",
                error_format_text="Pick a valid date.",
                error_invalid_text="Expiry date cannot be in the past.",
                entry_mode=ft.DatePickerEntryMode.CALENDAR_ONLY,
                on_change=handle_edit_date_change,
            )

            def open_edit_expiry_picker(e):
                selected_date = _parse_picker_date(expiry_field.value)
                edit_expiry_date_picker.value = selected_date or datetime.combine(date.today(), time.min)
                page.show_dialog(edit_expiry_date_picker)

            def clear_edit_expiry_date(e):
                set_edit_expiry_date_value("", update_page=True)

            async def pick_edit_image(e, state=edit_state, label=edit_image_label):
                def choose_file():
                    try:
                        import tkinter as tk
                        from tkinter import filedialog

                        root = tk.Tk()
                        root.withdraw()
                        root.attributes("-topmost", True)
                        file_path = filedialog.askopenfilename(
                            title="Choose updated donation image",
                            filetypes=[
                                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
                                ("All files", "*.*"),
                            ],
                        )
                        root.destroy()
                        return file_path
                    except Exception:
                        return None

                file_path = await asyncio.to_thread(choose_file)
                if file_path:
                    state["image_path"] = file_path
                    state["image_label"] = os.path.basename(file_path)
                label.value = state["image_label"]
                page.update()

            def begin_edit(e, state=edit_state, current_item=item):
                reset_donor_edit_state(current_item)
                donor_edit_state[current_item["id"]]["is_editing"] = True
                page.run_task(load_donations)

            def cancel_edit(e, state=edit_state, current_item=item):
                reset_donor_edit_state(current_item)
                page.run_task(load_donations)

            async def save_edit(
                e,
                donation_id=item["id"],
                state=edit_state,
                title_control=title_field,
                description_control=description_field,
                category_control=category_field,
                quantity_control=quantity_field,
                expiry_control=expiry_field,
            ):
                quantity_message = _validate_quantity(quantity_control.value)
                expiry_message = _validate_donation_date(expiry_control.value)
                _set_inline_error(quantity_control, quantity_field_error, quantity_message)
                _set_inline_error(expiry_control, expiry_field_error, expiry_message)
                page.update()

                if quantity_message or expiry_message:
                    show_error(page, "Please fix the highlighted donation fields.")
                    return

                quantity_value = int((quantity_control.value or "1").strip())

                state["title"] = title_control.value or ""
                state["description"] = description_control.value or ""
                state["category"] = category_control.value or "other"
                state["quantity"] = str(quantity_value)
                state["expiry_date"] = expiry_control.value or ""

                response = await asyncio.to_thread(
                    DonationService.update_donation,
                    donation_id,
                    title=state["title"],
                    description=state["description"],
                    category=state["category"],
                    quantity=quantity_value,
                    expiry_date=state["expiry_date"] or None,
                    image=state["image_path"],
                )

                if response.status_code in (200, 202):
                    show_success(page, "Donation updated successfully.")
                    state["is_editing"] = False
                    state["image_path"] = None
                    state["image_label"] = "Keep current image"
                    await load_donations()
                else:
                    show_error(page, f"Could not update donation: {response.text}")

            def confirm_delete(e, state=edit_state):
                state["confirming_delete"] = True
                page.run_task(load_donations)

            def cancel_delete(e, state=edit_state):
                state["confirming_delete"] = False
                page.run_task(load_donations)

            if edit_state["is_editing"]:
                controls.extend(
                    [
                        muted_text("Update your donation post below."),
                        title_field,
                        description_field,
                        category_field,
                        _field_block(quantity_field, quantity_field_error),
                        ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Container(content=expiry_field),
                                        secondary_button(
                                            "Pick Date",
                                            open_edit_expiry_picker,
                                            width=160,
                                            icon=ft.Icons.CALENDAR_MONTH,
                                        ),
                                        secondary_button(
                                            "Clear Date",
                                            clear_edit_expiry_date,
                                            width=160,
                                            icon=ft.Icons.CLOSE,
                                        ),
                                    ],
                                    wrap=True,
                                    spacing=4,
                                    vertical_alignment=ft.CrossAxisAlignment.END,
                                ),
                                expiry_field_error,
                            ],
                            spacing=4,
                        ),
                        ft.Container(
                            padding=16,
                            border_radius=16,
                            bgcolor="#FFFFFF",
                            border=ft.Border.all(1, "#D6E2D3"),
                            content=ft.Column(
                                [
                                    muted_text("Choose a new image only if you want to replace the current one."),
                                    ft.Row(
                                        [
                                            secondary_button(
                                                "Replace Image",
                                                pick_edit_image,
                                                width=170,
                                                icon=ft.Icons.UPLOAD_FILE,
                                            ),
                                            edit_image_label,
                                        ],
                                        wrap=True,
                                        spacing=12,
                                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    ),
                                ],
                                spacing=12,
                            ),
                        ),
                        ft.Row(
                            [
                                primary_button("Save Changes", save_edit, width=180, icon=ft.Icons.SAVE),
                                secondary_button("Cancel", cancel_edit, width=140, icon=ft.Icons.CLOSE),
                            ],
                            wrap=True,
                            spacing=12,
                        ),
                    ]
                )
                quantity_field.on_change = refresh_edit_form
                expiry_field.on_change = refresh_edit_form
                refresh_edit_form(update_page=False)
            else:
                controls.extend(
                    [
                        muted_text(f"Coordinates: {item.get('latitude')}, {item.get('longitude')}"),
                    ]
                )
                if edit_state["confirming_delete"]:
                    controls.append(
                        ft.Container(
                            padding=16,
                            border_radius=16,
                            bgcolor="#FFF4F2",
                            border=ft.Border.all(1, "#F3C7C0"),
                            content=ft.Column(
                                [
                                    ft.Text(
                                        "Delete Donation",
                                        size=16,
                                        weight=ft.FontWeight.BOLD,
                                        color="#7A271A",
                                    ),
                                    muted_text("Delete this donation post permanently?"),
                                    ft.Row(
                                        [
                                            secondary_button(
                                                "Cancel",
                                                cancel_delete,
                                                width=140,
                                                icon=ft.Icons.CLOSE,
                                            ),
                                            secondary_button(
                                                "Delete",
                                                lambda e, donation_id=item["id"]: page.run_task(delete_donation, donation_id),
                                                width=140,
                                                icon=ft.Icons.DELETE,
                                            ),
                                        ],
                                        wrap=True,
                                        spacing=12,
                                    ),
                                ],
                                spacing=12,
                            ),
                        )
                    )
                else:
                    controls.append(
                        ft.Row(
                            [
                                secondary_button("Edit Post", begin_edit, width=160, icon=ft.Icons.EDIT),
                                secondary_button("Delete Post", confirm_delete, width=160, icon=ft.Icons.DELETE),
                            ],
                            wrap=True,
                            spacing=12,
                        )
                    )
        else:
            message_field = auth_input("Claim message", ft.Icons.CHAT, multiline=True)
            claim_image_path = {"value": None}
            claim_image_label = ft.Text("No proof selected", color="#6B7280")

            def set_claim_image(file_path):
                claim_image_path["value"] = file_path
                claim_image_label.value = os.path.basename(file_path)

            async def select_claim_image_file(e):
                await pick_image_file(page, set_claim_image)

            async def select_claim_image_camera(e):
                await capture_image(page, set_claim_image)

            def handle_claim_click(e, donation_id=item["id"], field=message_field):
                page.run_task(claim_donation, donation_id, field, claim_image_path["value"])

            if status == "available":
                controls.extend(
                    [
                        message_field,
                        ft.Row(
                            [
                                secondary_button(
                                    "Upload Proof",
                                    select_claim_image_file,
                                    width=170,
                                    icon=ft.Icons.UPLOAD_FILE,
                                ),
                                secondary_button(
                                    "Take Photo",
                                    select_claim_image_camera,
                                    width=170,
                                    icon=ft.Icons.CAMERA_ALT,
                                ),
                                claim_image_label,
                            ],
                            wrap=True,
                            spacing=12,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        secondary_button("Claim Donation", handle_claim_click, width=220, icon=ft.Icons.SEND),
                    ]
                )
            else:
                controls.append(
                    muted_text("This donation is not available for claiming.")
                )

        return ft.Container(
            content=ft.Column(controls, spacing=10),
            padding=18,
            border=ft.Border.all(1, "#D6E2D3"),
            border_radius=18,
            bgcolor="#FFFEFB",
        )

    async def load_donations():
        response = await asyncio.to_thread(
            lambda: DonationService.get_donations(
                status=None if is_donor else "pending",
            )
        )
        donations_column.controls.clear()

        if response.status_code != 200:
            show_error(page, f"Failed to load donations: {response.text}")
            page.update()
            return

        items = response.json()
        filtered_items = [item for item in items if filter_matches(item)]

        if not filtered_items:
            donations_column.controls.append(
                ft.Container(
                    padding=20,
                    border_radius=12,
                    bgcolor="#FEF3F2",
                    border=ft.Border.all(1, "#FECACA"),
                    content=ft.Text(
                        no_results_message(),
                        color="#B42318",
                        size=14,
                        weight=ft.FontWeight.W_500,
                    ),
                )
            )
        else:
            for item in filtered_items:
                donations_column.controls.append(donation_card(item))
        page.update()

    def apply_category_filter(e):
        selected_category_filter["value"] = category_filter.value or "all"
        page.run_task(load_donations)


    def apply_status_filter(e):
        selected_status_filter["value"] = status_filter.value or "all"
        page.run_task(load_donations)


    def apply_filters():
        selected_category_filter["value"] = category_filter.value or "all"
        selected_status_filter["value"] = status_filter.value or "all"
        page.run_task(load_donations)


    def refresh_feed(e):
        hide_claim_notice()
        category_filter.value = "all"
        status_filter.value = "all"
        selected_category_filter["value"] = "all"
        selected_status_filter["value"] = "all"
        page.run_task(load_donations)

    async def pick_image_file(page, callback):
        picker = ft.FilePicker()
        files = await picker.pick_files(
            dialog_title="Choose image",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["png", "jpg", "jpeg", "gif", "bmp", "webp"],
            allow_multiple=False,
            with_data=False,
        )
        if files and files[0].path:
            callback(files[0].path)
        page.update()

    async def capture_image(page, callback):
        await pick_image_file(page, callback)

    async def pick_image(e):
        def on_file_selected(file_path):
            selected_image_path["value"] = file_path
            selected_image.value = os.path.basename(file_path)

        await pick_image_file(page, on_file_selected)
        if not selected_image_path["value"]:
            selected_image.value = "No image selected"
        page.update()

    async def create_donation(e):
        quantity_message = _validate_quantity(quantity.value)
        expiry_message = _validate_donation_date(expiry_date.value)
        _set_inline_error(quantity, quantity_error, quantity_message)
        _set_inline_error(expiry_date, expiry_date_error, expiry_message)
        page.update()

        title_message = None if title.value and title.value.strip() else "Title is required."
        description_message = None if description.value and description.value.strip() else "Description is required."
        _set_inline_error(title, title_error, title_message)
        _set_inline_error(description, description_error, description_message)

        if title_message or description_message or quantity_message or expiry_message:
            show_error(page, "Please fix the highlighted donation fields.")
            return

        try:
            response = await asyncio.to_thread(
                DonationService.create_donation,
                title=title.value,
                description=description.value,
                category=category.value,
                quantity=int((quantity.value or "1").strip()),
                expiry_date=expiry_date.value or None,
                latitude=None,
                longitude=None,
                image=selected_image_path["value"],
            )
        except Exception as ex:
            show_error(page, f"Error: {ex}")
            return

        if response.status_code in (200, 201):
            show_success(page, "Donation created successfully.")
            title.value = ""
            description.value = ""
            quantity.value = "1"
            set_create_expiry_date_value("", update_page=False)
            selected_image_path["value"] = None
            selected_image.value = "No image selected"
            refresh_create_form(update_page=False)
            await load_donations()
        else:
            show_error(page, f"Could not create donation: {response.text}")

    async def claim_donation(donation_id, message_field, proof_image=None):
        response = await asyncio.to_thread(
            DonationService.claim_donation,
            donation_id,
            message_field.value or "",
            image=proof_image,
        )
        if response.status_code in (200, 201):
            show_success(page, "Claim request sent.")
            message_field.value = ""
            claim_notice_state["token"] += 1
            claim_notice.visible = True
            claim_notice.content = ft.Column(
                [
                    ft.Text(
                        "Claim Request Sent",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color="#166534",
                    ),
                    muted_text("Your request has been sent to the donor. You can track it from My Claims."),
                ],
                spacing=8,
            )
            await load_donations()
            page.run_task(auto_hide_claim_notice, claim_notice_state["token"])
        else:
            show_error(page, f"Could not claim donation: {response.text}")

    async def delete_donation(donation_id):
        response = await asyncio.to_thread(DonationService.delete_donation, donation_id)
        if response.status_code in (200, 202, 204):
            donor_edit_state.pop(donation_id, None)
            show_success(page, "Donation deleted successfully.")
            await load_donations()
        else:
            if donation_id in donor_edit_state:
                donor_edit_state[donation_id]["confirming_delete"] = False
            show_error(page, f"Could not delete donation: {response.text}")

    async def go_back(e):
        await page.push_route("/dashboard")

    create_controls = []
    if is_donor:
        title.on_change = refresh_create_form
        description.on_change = refresh_create_form
        quantity.on_change = refresh_create_form
        expiry_date.on_change = refresh_create_form
        refresh_create_form(update_page=False)
        create_controls = [
            section_card(
                "Create Donation",
                [
                    muted_text("Add the donation details below and optionally attach an image."),
                    _field_block(title, title_error),
                    _field_block(description, description_error),
                    category,
                    _field_block(quantity, quantity_error),
                    ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Container(content=expiry_date),
                                    secondary_button(
                                        "Pick Date",
                                        open_create_expiry_picker,
                                        width=160,
                                        icon=ft.Icons.CALENDAR_MONTH,
                                    ),
                                    secondary_button(
                                        "Clear Date",
                                        clear_create_expiry_date,
                                        width=160,
                                        icon=ft.Icons.CLOSE,
                                    ),
                                ],
                                wrap=True,
                                spacing=12,
                                vertical_alignment=ft.CrossAxisAlignment.END,
                            ),
                            expiry_date_error,
                        ],
                        spacing=4,
                    ),
                    ft.Container(
                        padding=16,
                        border_radius=16,
                        bgcolor="#FFFFFF",
                        border=ft.Border.all(1, "#D6E2D3"),
                        content=ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Icon(ft.Icons.IMAGE, color="#6A994E"),
                                        ft.Text("Donation Image", size=16, weight=ft.FontWeight.BOLD, color="#1F2937"),
                                    ],
                                    spacing=10,
                                ),
                                muted_text("Choose an optional image from your device."),
                                ft.Row(
                                    [
                                        secondary_button(
                                            "Upload Image",
                                            pick_image,
                                            width=170,
                                            icon=ft.Icons.UPLOAD_FILE,
                                        ),
                                        secondary_button(
                                            "Take Photo",
                                            lambda e: page.run_task(
                                                capture_image,
                                                page,
                                                lambda file_path: (
                                                    selected_image_path.__setitem__("value", file_path),
                                                    setattr(selected_image, "value", os.path.basename(file_path)),
                                                    page.update(),
                                                ),
                                            ),
                                            width=170,
                                            icon=ft.Icons.CAMERA_ALT,
                                        ),
                                        selected_image,
                                    ],
                                    wrap=True,
                                    spacing=12,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                ),
                            ],
                            spacing=12,
                        ),
                    ),
                    primary_button("Create Donation", create_donation, width=220, icon=ft.Icons.ADD_CIRCLE),
                ],
                subtitle="Only donors can create new donation posts.",
            ),
        ]

    page.run_task(load_donations)

    feed_title = "All Donation Posts" if is_donor else "Available Donations"
    feed_subtitle = (
        "Browse all donation posts and track their status: available or pending."
        if is_donor
        else "Browse active donations and send a claim request."
    )

    return ft.View(
        route="/donations",
        appbar=build_appbar("Donations", go_back),
        controls=[
            page_container(
                *create_controls,
                ft.Column(
                    controls=[
                        section_card(
                            feed_title,
                            [
                                muted_text(feed_subtitle),
                                ft.Row(
                                    [
                                        category_filter,
                                        status_filter,
                                        primary_button(
                                            "Apply Filters",
                                            lambda e: apply_filters(),
                                            width=180,
                                            icon=ft.Icons.FILTER_LIST,
                                        ),
                                        secondary_button(
                                            "Refresh",
                                            refresh_feed,
                                            width=140,
                                            icon=ft.Icons.REFRESH,
                                        ),
                                    ],
                                    spacing=12,
                                    wrap=True,
                                ),
                                claim_notice,
                                donations_column,
                            ],
                        ),
                    ],
                    spacing=20,
                    expand=True,
                ),
            ),
        ],
    )
