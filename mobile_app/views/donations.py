import flet as ft

from services.auth_service import AuthService
from services.donation_service import DonationService
from utils.constants import PRIMARY_GREEN, SECONDARY_GREEN, BUTTON_TEXT, INPUT_TEXT
from utils.helpers import show_message


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
    latitude = ft.TextField(label="Latitude", color=INPUT_TEXT)
    longitude = ft.TextField(label="Longitude", color=INPUT_TEXT)
    image_path = ft.TextField(label="Image Path (optional)", color=INPUT_TEXT)
    claim_message = ft.TextField(label="Claim message", multiline=True, min_lines=2, color=INPUT_TEXT)

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
            controls.extend(
                [
                    message_field,
                    ft.Button(
                        "Claim Donation",
                        on_click=lambda e, donation_id=item["id"], field=message_field: claim_donation(donation_id, field),
                        bgcolor=SECONDARY_GREEN,
                        color=BUTTON_TEXT,
                    ),
                ]
            )

        return ft.Container(
            content=ft.Column(controls, spacing=8),
            padding=15,
            border=ft.border.all(1, "#d9d9d9"),
            border_radius=12,
        )

    def load_donations():
        response = DonationService.get_my_donations() if is_donor else DonationService.get_donations()
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

    def create_donation(e):
        try:
            response = DonationService.create_donation(
                title=title.value,
                description=description.value,
                category=category.value,
                quantity=int(quantity.value or "1"),
                expiry_date=expiry_date.value or None,
                latitude=latitude.value or None,
                longitude=longitude.value or None,
                image=image_path.value or None,
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
            latitude.value = ""
            longitude.value = ""
            image_path.value = ""
            load_donations()
        else:
            show_message(page, f"Could not create donation: {response.text}", "red")

    def claim_donation(donation_id, message_field):
        response = DonationService.claim_donation(donation_id, message_field.value or "")
        if response.status_code in (200, 201):
            show_message(page, "Claim request sent.", "green")
            message_field.value = ""
            load_donations()
        else:
            show_message(page, f"Could not claim donation: {response.text}", "red")

    async def go_back(e):
        await page.push_route("/dashboard")

    create_controls = []
    if is_donor:
        create_controls = [
            ft.Text("Create Donation", size=20, weight=ft.FontWeight.BOLD),
            title,
            description,
            category,
            quantity,
            expiry_date,
            latitude,
            longitude,
            image_path,
            ft.Button("Create", on_click=create_donation, bgcolor=PRIMARY_GREEN, color=BUTTON_TEXT),
            ft.Divider(),
        ]

    load_donations()

    return ft.View(
        route="/donations",
        appbar=ft.AppBar(title=ft.Text("Donations")),
        controls=[
            ft.Container(
                expand=True,
                padding=20,
                content=ft.Column(
                    create_controls
                    + [
                        ft.Row(
                            [
                                ft.Text("Donation Feed", size=20, weight=ft.FontWeight.BOLD),
                                ft.Button("Refresh", on_click=lambda e: load_donations(), bgcolor=SECONDARY_GREEN, color=BUTTON_TEXT),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        donations_column,
                        ft.Button("Back", on_click=go_back, bgcolor="#666666", color=BUTTON_TEXT),
                    ],
                    spacing=15,
                    expand=True,
                ),
            )
        ],
    )
