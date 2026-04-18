import flet as ft

from services.auth_service import AuthService
from services.claim_service import ClaimService
from utils.constants import PRIMARY_GREEN, SECONDARY_GREEN, BUTTON_TEXT
from utils.helpers import build_appbar, page_container, section_card, show_message


def claims_view(page: ft.Page):
    claims_column = ft.Column(spacing=12, scroll=ft.ScrollMode.AUTO, expand=True)
    is_donor = AuthService.user and AuthService.user.get("role") == "donor"

    def refresh_claims(claim_type=None):
        if claim_type == "received":
            response = ClaimService.get_received_claims()
        elif claim_type == "sent":
            response = ClaimService.get_sent_claims()
        else:
            response = ClaimService.get_my_claims()

        claims_column.controls.clear()
        if response.status_code != 200:
            show_message(page, f"Failed to load claims: {response.text}", "red")
            page.update()
            return

        claims = response.json()
        if not claims:
            claims_column.controls.append(ft.Text("No claims available."))
        else:
            for claim in claims:
                donation = claim.get("donation") or {}
                receiver = claim.get("receiver") or {}
                controls = [
                    ft.Text(donation.get("title", "Donation"), size=18, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Status: {claim.get('status', 'unknown')}"),
                    ft.Text(f"NGO: {receiver.get('email', 'Unknown')}"),
                    ft.Text(f"Message: {claim.get('message') or 'No message provided'}"),
                ]

                if is_donor and claim.get("status") == "pending":
                    controls.append(
                        ft.Row(
                            [
                                ft.Button(
                                    "Accept",
                                    on_click=lambda e, claim_id=claim["id"]: accept_claim(claim_id),
                                    bgcolor=PRIMARY_GREEN,
                                    color=BUTTON_TEXT,
                                ),
                                ft.Button(
                                    "Reject",
                                    on_click=lambda e, claim_id=claim["id"]: reject_claim(claim_id),
                                    bgcolor="#b23a48",
                                    color=BUTTON_TEXT,
                                ),
                            ]
                        )
                    )

                claims_column.controls.append(
                    section_card("Claim Details", controls)
                )
        page.update()

    def accept_claim(claim_id):
        response = ClaimService.accept_claim(claim_id)
        if response.status_code == 200:
            show_message(page, "Claim accepted.", "green")
            refresh_claims("received")
        else:
            show_message(page, f"Could not accept claim: {response.text}", "red")

    def reject_claim(claim_id):
        response = ClaimService.reject_claim(claim_id)
        if response.status_code == 200:
            show_message(page, "Claim rejected.", "green")
            refresh_claims("received")
        else:
            show_message(page, f"Could not reject claim: {response.text}", "red")

    async def go_back(e):
        await page.push_route("/dashboard")

    refresh_claims("received" if is_donor else "sent")

    return ft.View(
        route="/claims",
        appbar=build_appbar("Claim Requests", go_back),
        controls=[
            page_container(
                section_card(
                    "Filters",
                    [
                        ft.Row(
                            [
                                ft.Button("All", on_click=lambda e: refresh_claims(), bgcolor=SECONDARY_GREEN, color=BUTTON_TEXT),
                                ft.Button("Received", on_click=lambda e: refresh_claims("received"), bgcolor=SECONDARY_GREEN, color=BUTTON_TEXT),
                                ft.Button("Sent", on_click=lambda e: refresh_claims("sent"), bgcolor=SECONDARY_GREEN, color=BUTTON_TEXT),
                            ]
                            if is_donor
                            else [
                                ft.Button("Sent Claims", on_click=lambda e: refresh_claims("sent"), bgcolor=SECONDARY_GREEN, color=BUTTON_TEXT),
                            ],
                            wrap=True,
                            spacing=12,
                        ),
                    ],
                ),
                claims_column,
                ft.Row(
                    [ft.Button("Back", on_click=go_back, bgcolor="#666666", color=BUTTON_TEXT, width=140)],
                    alignment=ft.MainAxisAlignment.END,
                ),
            ),
        ],
    )
