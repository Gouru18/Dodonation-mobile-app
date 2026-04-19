import flet as ft

from services.auth_service import AuthService
from services.claim_service import ClaimService
from utils.helpers import (
    build_appbar,
    page_container,
    centered_content,
    section_card,
    primary_button,
    secondary_button,
    muted_text,
    status_chip,
    show_error,
    show_success,
)


def claims_view(page: ft.Page):
    user = AuthService.user or {}
    is_donor = user.get("role") == "donor"

    claims_column = ft.Column(spacing=12, scroll=ft.ScrollMode.AUTO, expand=True)
    selected_filter = {"value": "received" if is_donor else "sent"}

    def status_color(value):
        mapping = {
            "pending": "#B54708",
            "accepted": "#027A48",
            "rejected": "#B42318",
        }
        return mapping.get((value or "").lower(), "#667085")

    def filter_label(filter_name):
        if filter_name == "received":
            return "Received Claims"
        if filter_name == "sent":
            return "Sent Claims"
        return "All Claims"

    def claim_card(claim):
        donation = claim.get("donation") or {}
        receiver = claim.get("receiver") or {}
        donor = donation.get("donor") or {}
        claim_status = (claim.get("status") or "unknown").lower()
        donation_status = (donation.get("status") or "unknown").lower()

        top_row = ft.Row(
            [
                ft.Text(
                    donation.get("title", "Donation"),
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color="#1F2937",
                    expand=True,
                ),
                status_chip(f"Claim: {claim_status}", color=status_color(claim_status)),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        meta_chips = ft.Row(
            [
                status_chip(f"Category: {donation.get('category', 'n/a')}", color="#1D4ED8"),
                status_chip(f"Qty: {donation.get('quantity', 1)}", color="#027A48"),
                status_chip(f"Donation Status: {donation.get('status', 'unknown')}", color="#667085"),
            ],
            wrap=True,
            spacing=8,
        )

        details = [
            top_row,
            muted_text(donation.get("description") or "No donation description."),
            meta_chips,
        ]

        if is_donor:
            details.append(muted_text(f"NGO: {receiver.get('email', 'Unknown NGO')}"))
        else:
            details.append(muted_text(f"Donor: {donor.get('email', 'Unknown donor')}"))

        details.extend(
            [
                muted_text(f"Message: {claim.get('message') or 'No message provided'}"),
            ]
        )

        if claim.get("date_responded"):
            details.append(muted_text(f"Responded at: {claim.get('date_responded')}"))

        if is_donor and claim_status == "pending":
            details.append(
                ft.Row(
                    [
                        primary_button(
                            "Accept",
                            lambda e, claim_id=claim["id"]: accept_claim(claim_id),
                            width=140,
                            icon=ft.Icons.CHECK_CIRCLE,
                        ),
                        secondary_button(
                            "Reject",
                            lambda e, claim_id=claim["id"]: reject_claim(claim_id),
                            width=140,
                            icon=ft.Icons.CANCEL,
                        ),
                    ],
                    wrap=True,
                    spacing=12,
                )
            )

        if donation_status == "completed":
            details.append(
                ft.Row(
                    [
                        secondary_button(
                            "Delete Claim Request",
                            lambda e, claim_id=claim["id"]: delete_claim(claim_id),
                            width=220,
                            icon=ft.Icons.DELETE,
                        ),
                    ],
                    wrap=True,
                    spacing=12,
                )
            )

        return ft.Container(
            content=ft.Column(details, spacing=10),
            padding=18,
            border=ft.Border.all(1, "#D6E2D3"),
            border_radius=18,
            bgcolor="#FFFEFB",
        )

    def refresh_claims(claim_type=None):
        selected_filter["value"] = claim_type or "all"

        if claim_type == "received":
            response = ClaimService.get_received_claims()
        elif claim_type == "sent":
            response = ClaimService.get_sent_claims()
        else:
            response = ClaimService.get_my_claims()

        claims_column.controls.clear()

        if response.status_code != 200:
            show_error(page, f"Failed to load claims: {response.text}")
            page.update()
            return

        claims = response.json()

        if not claims:
            claims_column.controls.append(
                muted_text(f"No {filter_label(selected_filter['value']).lower()} available.")
            )
        else:
            for claim in claims:
                claims_column.controls.append(claim_card(claim))

        page.update()

    def accept_claim(claim_id):
        response = ClaimService.accept_claim(claim_id)
        if response.status_code == 200:
            show_success(page, "Claim accepted.")
            refresh_claims("received")
        else:
            show_error(page, f"Could not accept claim: {response.text}")

    def reject_claim(claim_id):
        response = ClaimService.reject_claim(claim_id)
        if response.status_code == 200:
            show_success(page, "Claim rejected.")
            refresh_claims("received")
        else:
            show_error(page, f"Could not reject claim: {response.text}")

    def delete_claim(claim_id):
        response = ClaimService.delete_claim(claim_id)
        if response.status_code in (200, 202, 204):
            show_success(page, "Claim request deleted.")
            refresh_claims(selected_filter["value"])
        else:
            show_error(page, f"Could not delete claim request: {response.text}")

    async def go_back(e):
        await page.push_route("/dashboard")

    refresh_claims("received" if is_donor else "sent")

    filter_buttons = (
        [
            secondary_button("All", lambda e: refresh_claims(), width=120, icon=ft.Icons.LIST),
            secondary_button("Received", lambda e: refresh_claims("received"), width=140, icon=ft.Icons.INBOX),
        ]
        if is_donor
        else []
    )

    return ft.View(
        route="/claims",
        appbar=build_appbar("Claim Requests", go_back),
        controls=[
            page_container(
                centered_content(
                    section_card(
                        "Claims",
                        [
                            muted_text(
                                "Review claim requests linked to donation posts."
                                if is_donor
                                else "Track the claims you have sent to donors."
                            ),
                            ft.Row(
                                filter_buttons,
                                wrap=True,
                                spacing=12,
                            ),
                            muted_text(f"Showing: {filter_label(selected_filter['value'])}"),
                        ],
                    ),
                    section_card(
                        "Claim List",
                        [claims_column],
                    ),
                    ft.Row(
                        [
                            secondary_button(
                                "Back",
                                go_back,
                                width=140,
                                icon=ft.Icons.ARROW_BACK,
                            )
                        ],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                )
            ),
        ],
    )
