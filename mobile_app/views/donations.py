import asyncio
import os
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


def donations_view(page: ft.Page):
    is_donor = AuthService.user and AuthService.user.get("role") == "donor"
    donations_column = ft.Column(spacing=12, scroll=ft.ScrollMode.AUTO, expand=True)
    media_base_url = BASE_URL.rsplit("/api", 1)[0]
    image_fit_cover = getattr(getattr(ft, "ImageFit", None), "COVER", "cover")

    def show_claim_sent_alert():
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Claim Request Sent"),
            content=ft.Text("Your claim request has been sent to the donor successfully."),
            actions=[
                ft.TextButton(
                    "OK",
                    on_click=lambda e: close_claim_sent_alert(dialog),
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        if hasattr(page, "open"):
            page.open(dialog)
            return

        page.dialog = dialog
        if hasattr(page, "overlay") and dialog not in page.overlay:
            page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def close_claim_sent_alert(dialog):
        if hasattr(page, "close"):
            page.close(dialog)
            return

        dialog.open = False
        if hasattr(page, "overlay") and dialog in page.overlay:
            page.overlay.remove(dialog)
        page.update()

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
    expiry_date = auth_input("Expiry Date (YYYY-MM-DD)", ft.Icons.CALENDAR_MONTH)

    selected_image = ft.Text("No image selected", color="#6B7280")
    selected_image_path = {"value": None}

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
        normalized_status = (item.get("feed_status") or item.get("status") or "available").strip().lower()
        if normalized_status == "completed":
            return "claimed"
        if normalized_status == "expired":
            return "rejected"
        return normalized_status

    def status_color(status):
        return {
            "available": "#027A48",
            "claimed": "#1D4ED8",
            "expired": "#B54708",
            "rejected": "#B42318",
        }.get(status, "#667085")

    def donation_card(item):
        donor_data = item.get("donor") or {}
        status = donor_feed_status(item) if is_donor else display_status(item.get("status"))
        image_src = resolve_image_src(item)

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
            controls.append(
                muted_text(f"Coordinates: {item.get('latitude')}, {item.get('longitude')}")
            )
        else:
            message_field = auth_input("Claim message", ft.Icons.CHAT, multiline=True)

            def handle_claim_click(e, donation_id=item["id"], field=message_field):
                page.run_task(claim_donation, donation_id, field)

            controls.extend(
                [
                    message_field,
                    secondary_button("Claim Donation", handle_claim_click, width=220, icon=ft.Icons.SEND),
                ]
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
            DonationService.get_donations if is_donor else (lambda: DonationService.get_donations(status="pending"))
        )
        donations_column.controls.clear()

        if response.status_code != 200:
            show_error(page, f"Failed to load donations: {response.text}")
            page.update()
            return

        items = response.json()
        if not items:
            donations_column.controls.append(
                muted_text("No donations found yet.")
            )
        else:
            for item in items:
                donations_column.controls.append(donation_card(item))
        page.update()

    async def pick_image(e):
        def choose_file():
            try:
                import tkinter as tk
                from tkinter import filedialog

                root = tk.Tk()
                root.withdraw()
                root.attributes("-topmost", True)
                file_path = filedialog.askopenfilename(
                    title="Choose donation image",
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
            selected_image_path["value"] = file_path
            selected_image.value = os.path.basename(file_path)
        else:
            selected_image.value = "No image selected"
        page.update()

    async def create_donation(e):
        try:
            response = await asyncio.to_thread(
                DonationService.create_donation,
                title=title.value,
                description=description.value,
                category=category.value,
                quantity=int(quantity.value or "1"),
                expiry_date=expiry_date.value or None,
                latitude=None,
                longitude=None,
                image=selected_image_path["value"],
            )
        except ValueError:
            show_error(page, "Quantity must be a number.")
            return
        except Exception as ex:
            show_error(page, f"Error: {ex}")
            return

        if response.status_code in (200, 201):
            show_success(page, "Donation created successfully.")
            title.value = ""
            description.value = ""
            quantity.value = "1"
            expiry_date.value = ""
            selected_image_path["value"] = None
            selected_image.value = "No image selected"
            await load_donations()
        else:
            show_error(page, f"Could not create donation: {response.text}")

    async def claim_donation(donation_id, message_field):
        response = await asyncio.to_thread(
            DonationService.claim_donation,
            donation_id,
            message_field.value or ""
        )
        if response.status_code in (200, 201):
            show_success(page, "Claim request sent.")
            message_field.value = ""
            await load_donations()
            show_claim_sent_alert()
        else:
            show_error(page, f"Could not claim donation: {response.text}")

    async def go_back(e):
        await page.push_route("/dashboard")

    create_controls = []
    if is_donor:
        create_controls = [
            section_card(
                "Create Donation",
                [
                    muted_text("Add the donation details below and optionally attach an image."),
                    title,
                    description,
                    category,
                    quantity,
                    expiry_date,
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
                                        secondary_button("Upload Image", pick_image, width=170, icon=ft.Icons.UPLOAD_FILE),
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
        "Browse all donation posts. Donors can review statuses but cannot claim."
        if is_donor
        else "Browse active donations and send a claim request."
    )

    return ft.View(
        route="/donations",
        appbar=build_appbar("Donations", go_back),
        controls=[
            page_container(
                centered_content(
                    *create_controls,
                    section_card(
                        feed_title,
                        [
                            ft.Row(
                                [
                                    muted_text(feed_subtitle),
                                    secondary_button(
                                        "Refresh",
                                        lambda e: page.run_task(load_donations),
                                        width=140,
                                        icon=ft.Icons.REFRESH,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                wrap=True,
                            ),
                            donations_column,
                        ],
                    ),
                )
            ),
        ],
    )
