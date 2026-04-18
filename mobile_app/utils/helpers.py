# pylint: disable=E1121, E1123
import flet as ft

PAGE_BG = "#F4F7F1"
CARD_BG = "#FFFEFB"
CARD_BORDER = "#D6E2D3"
TEXT_MUTED = "#6B7280"

def form_container(title, controls):
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(title, size=28, weight=ft.FontWeight.BOLD, color="#1F2937"),
                ft.Text(
                    "Share with care, coordinate with confidence.",
                    size=13,
                    color=TEXT_MUTED,
                ),
                ft.Divider(color=CARD_BORDER),
                *controls
            ],
            spacing=15
        ),
        padding=24,
        width=360,
        bgcolor=CARD_BG,
        border=ft.Border.all(1, CARD_BORDER),
        border_radius=24,
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=18,
            color="#00000014",
            offset=ft.Offset(0, 8),
        ),
    )


def auth_scaffold(page, route, title, card):
    return ft.View(
        route=route,
        appbar=ft.AppBar(
            title=ft.Text(title, color="#1F2937"),
            bgcolor=PAGE_BG,
        ),
        bgcolor=PAGE_BG,
        controls=[
            ft.Container(
                expand=True,
                padding=24,
                content=ft.Stack(
                    [
                        ft.Container(
                            expand=True,
                            border_radius=36,
                            gradient=ft.LinearGradient(
                                colors=[PAGE_BG, "#E6EFE1", "#FDFCF8"],
                            ),
                        ),
                        ft.Container(
                            expand=True,
                            alignment=ft.Alignment(0, 0),
                            content=ft.Column(
                                [card],
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                scroll=ft.ScrollMode.AUTO,
                            ),
                        ),
                    ],
                    expand=True,
                ),
            )
        ],
    )


def build_appbar(title, on_back=None):
    leading = None
    if on_back is not None:
        leading = ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=on_back, icon_color="#1F2937")
    return ft.AppBar(
        title=ft.Text(title, color="#1F2937", weight=ft.FontWeight.BOLD),
        leading=leading,
        bgcolor=PAGE_BG,
    )


def page_container(*controls, expand=True, scroll=ft.ScrollMode.AUTO):
    return ft.Container(
        expand=expand,
        padding=24,
        content=ft.Column(
            list(controls),
            spacing=18,
            scroll=scroll,
            expand=expand,
        ),
    )


def centered_content(*controls, max_width=980):
    return ft.Container(
        alignment=ft.Alignment(0, -1),
        expand=True,
        content=ft.Container(
            width=max_width,
            content=ft.Column(list(controls), spacing=18, expand=False),
        ),
    )


def section_card(title, controls, subtitle=None):
    items = [ft.Text(title, size=22, weight=ft.FontWeight.BOLD, color="#1F2937")]
    if subtitle:
        items.append(ft.Text(subtitle, size=13, color=TEXT_MUTED))
    items.extend(controls)
    return ft.Container(
        padding=20,
        bgcolor=CARD_BG,
        border=ft.Border.all(1, CARD_BORDER),
        border_radius=20,
        content=ft.Column(items, spacing=14),
    )

def show_message(page, msg, color="green"):
    page.snack_bar = ft.SnackBar(
        ft.Text(msg),
        bgcolor=color
    )
    page.snack_bar.open = True
    page.update()


def clear_page(page):
    page.controls.clear()
