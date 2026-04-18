import asyncio
import flet as ft

from services.auth_service import AuthService
from services.donation_service import DonationService
from utils.constants import PRIMARY_GREEN, SECONDARY_GREEN, BUTTON_TEXT, INPUT_TEXT
from utils.helpers import build_appbar, page_container, section_card, show_message


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

    title = ft.TextField(label="Title", color=INPUT_TEXT)
    description = ft.TextField(label="Description", multiline=True, min_lines=3, color=INPUT_TEXT)
    category = ft.Dropdown(label="Category", options=CATEGORY_OPTIONS, value="other")
    quantity = ft.TextField(label="Quantity", value="1", color=INPUT_TEXT)
    expiry_date = ft.TextField(label="Expiry Date (YYYY-MM-DD)", color=INPUT_TEXT)
    selected_image = ft.Text("No image selected", color="#6B7280")
    selected_image_path = {"value": None}

    def donation_card(item):
        donor_data = item.get("donor") or {}
        controls = [
            ft.Text(item.get("title", "Untitled"), size=18, weight=ft.FontWeight.BOLD),
            ft.Text(item.get("description", "")),
            ft.Text(f"Category: {item.get('category', 'n/a')} | Qty: {item.get('quantity', 1)}"),
            ft.Text(f"Status: {item.get('status', 'n/a')}"),
            ft.Text(f"Donor: {donor_data.get('email', 'Unknown')}"),
        ]

        if is_donor:
            controls.append(ft.Text(f"Coordinates: {item.get('latitude')}, {item.get('longitude')}"))
        else:
            message_field = ft.TextField(label="Claim message", multiline=True, min_lines=2, color=INPUT_TEXT)

            def handle_claim_click(e, donation_id=item["id"], field=message_field):
                page.run_task(claim_donation, donation_id, field)

            controls.extend(
                [
                    message_field,
                    ft.Button(
                        "Claim Donation",
                        on_click=handle_claim_click,
                        bgcolor=SECONDARY_GREEN,
                        color=BUTTON_TEXT,
                    ),
                ]
            )

        return ft.Container(
            content=ft.Column(controls, spacing=8),
            padding=15,
            border=ft.Border.all(1, "#d9d9d9"),
            border_radius=12,
            bgcolor="#FFFEFB",
        )

    async def load_donations():
        response = await asyncio.to_thread(
            DonationService.get_my_donations if is_donor else DonationService.get_donations
        )
        donations_column.controls.clear()

        if response.status_code != 200:
            show_message(page, f"Failed to load donations: {response.text}", "red")
            page.update()
            return

        items = response.json()
        if not items:
            donations_column.controls.append(ft.Text("No donations found yet."))
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
            import os
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
            show_message(page, "Quantity must be a number.", "red")
            return
        except Exception as ex:
            show_message(page, f"Error: {ex}", "red")
            return

        if response.status_code in (200, 201):
            show_message(page, "Donation created successfully.", "green")
            title.value = ""
            description.value = ""
            quantity.value = "1"
            expiry_date.value = ""
            selected_image_path["value"] = None
            selected_image.value = "No image selected"
            await load_donations()
        else:
            show_message(page, f"Could not create donation: {response.text}", "red")

    async def claim_donation(donation_id, message_field):
        response = await asyncio.to_thread(DonationService.claim_donation, donation_id, message_field.value or "")
        if response.status_code in (200, 201):
            show_message(page, "Claim request sent.", "green")
            message_field.value = ""
            await load_donations()
        else:
            show_message(page, f"Could not claim donation: {response.text}", "red")

    async def go_back(e):
        await page.push_route("/dashboard")

    create_controls = []
    if is_donor:
        create_controls = [
            section_card(
                "Create Donation",
                [
                    title,
                    description,
                    category,
                    quantity,
                    expiry_date,
                    ft.Row(
                        [
                            ft.Button("Upload Image", on_click=pick_image, bgcolor=SECONDARY_GREEN, color=BUTTON_TEXT),
                            selected_image,
                        ],
                        wrap=True,
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Button("Create Donation", on_click=create_donation, bgcolor=PRIMARY_GREEN, color=BUTTON_TEXT, width=180),
                ],
                subtitle="Add the item details and optionally attach an image from your device.",
            ),
        ]

    page.run_task(load_donations)

    return ft.View(
        route="/donations",
        appbar=build_appbar("Donations", go_back),
        controls=[
            page_container(
                *create_controls,
                section_card(
                    "Donation Feed",
                    [
                        ft.Row(
                            [
                                ft.Text("Browse current donations", color="#4B5563"),
                                ft.Button("Refresh", on_click=lambda e: page.run_task(load_donations), bgcolor=SECONDARY_GREEN, color=BUTTON_TEXT),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        donations_column,
                    ],
                ),
                ft.Row(
                    [ft.Button("Back", on_click=go_back, bgcolor="#666666", color=BUTTON_TEXT, width=140)],
                    alignment=ft.MainAxisAlignment.END,
                ),
            ),
        ],
    )
