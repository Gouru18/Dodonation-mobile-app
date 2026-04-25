# pylint: disable=E1121, E1123
import flet as ft
from utils.constants import (
    PRIMARY_GREEN,
    SECONDARY_GREEN,
    PAGE_BG,
    CARD_BG,
    CARD_BORDER,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TEXT_MUTED,
    BUTTON_TEXT,
    INPUT_TEXT,
    INPUT_BG,
    SUCCESS,
    DANGER,
    INFO,
    RADIUS_LG,
    RADIUS_MD,
    RADIUS_SM,
    SPACE_SM,
    SPACE_MD,
    SPACE_LG,
    SPACE_XL,
    AUTH_CARD_WIDTH,
    AUTH_BUTTON_WIDTH,
)


def primary_button(text, on_click, width=AUTH_BUTTON_WIDTH, icon=None):
    return ft.Button(
        text,
        on_click=on_click,
        width=width,
        height=46,
        icon=icon,
        style=ft.ButtonStyle(
            bgcolor=PRIMARY_GREEN,
            color=BUTTON_TEXT,
            shape=ft.RoundedRectangleBorder(radius=RADIUS_SM),
        ),
    )


def secondary_button(text, on_click, width=AUTH_BUTTON_WIDTH, icon=None):
    return ft.Button(
        text,
        on_click=on_click,
        width=width,
        height=46,
        icon=icon,
        style=ft.ButtonStyle(
            bgcolor=SECONDARY_GREEN,
            color=BUTTON_TEXT,
            shape=ft.RoundedRectangleBorder(radius=RADIUS_SM),
        ),
    )


def subtle_text_button(text, on_click):
    return ft.TextButton(
        text,
        on_click=on_click,
        style=ft.ButtonStyle(color=SECONDARY_GREEN),
    )


def auth_input(label, icon=None, password=False, multiline=False):
    return ft.TextField(
        label=label,
        prefix_icon=icon,
        password=password,
        can_reveal_password=password,
        multiline=multiline,
        color=INPUT_TEXT,
        border_radius=RADIUS_SM,
        filled=True,
        bgcolor=INPUT_BG,
        border_color=CARD_BORDER,
        focused_border_color=PRIMARY_GREEN,
        error_style=ft.TextStyle(color=DANGER, size=12),
        content_padding=ft.Padding.symmetric(horizontal=14, vertical=14),
    )


def helper_text(text):
    return ft.Text(text, size=14, color=TEXT_SECONDARY)


def muted_text(text, size=13, text_align=None):
    return ft.Text(text, size=size, color=TEXT_MUTED, text_align=text_align)


def section_header(title, subtitle=None):
    items = [
        ft.Text(title, size=28, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
    ]
    if subtitle:
        items.append(ft.Text(subtitle, size=13, color=TEXT_MUTED))
    return ft.Column(items, spacing=4)


def form_container(title, controls, subtitle="Share with care, coordinate with confidence."):
    return ft.Container(
        content=ft.Column(
            controls=[
                section_header(title, subtitle),
                ft.Divider(color=CARD_BORDER),
                *controls,
            ],
            spacing=SPACE_MD,
        ),
        padding=28,
        width=AUTH_CARD_WIDTH,
        bgcolor=CARD_BG,
        border=ft.Border.all(1, CARD_BORDER),
        border_radius=RADIUS_LG,
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=18,
            color="#00000012",
            offset=ft.Offset(0, 8),
        ),
    )


def auth_scaffold(page, route, title, card):
    return ft.View(
        route=route,
        appbar=ft.AppBar(
            title=ft.Text(title, color=TEXT_PRIMARY, weight=ft.FontWeight.BOLD),
            bgcolor=PAGE_BG,
        ),
        bgcolor=PAGE_BG,
        controls=[
            ft.Container(
                expand=True,
                padding=SPACE_XL,
                content=ft.Stack(
                    [
                        ft.Container(
                            expand=True,
                            border_radius=36,
                            gradient=ft.LinearGradient(
                                colors=[PAGE_BG, "#EAF2E6", "#FDFCF8"],
                                begin=ft.Alignment.TOP_CENTER,
                                end=ft.Alignment.BOTTOM_CENTER,
                            ),
                        ),
                        ft.Container(
                            expand=True,
                            alignment=ft.Alignment.CENTER,
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
        leading = ft.IconButton(
            icon=ft.Icons.ARROW_BACK,
            on_click=on_back,
            icon_color=TEXT_PRIMARY,
        )
    return ft.AppBar(
        title=ft.Text(title, color=TEXT_PRIMARY, weight=ft.FontWeight.BOLD),
        leading=leading,
        bgcolor=PAGE_BG,
    )


def page_container(*controls, expand=True, scroll=ft.ScrollMode.AUTO):
    return ft.Container(
        expand=expand,
        padding=SPACE_XL,
        content=ft.Column(
            list(controls),
            spacing=SPACE_LG,
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
            content=ft.Column(list(controls), spacing=SPACE_LG, expand=False),
        ),
    )


def section_card(title, controls, subtitle=None):
    items = [ft.Text(title, size=22, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY)]
    if subtitle:
        items.append(ft.Text(subtitle, size=13, color=TEXT_MUTED))
    items.extend(controls)
    return ft.Container(
        padding=20,
        bgcolor=CARD_BG,
        border=ft.Border.all(1, CARD_BORDER),
        border_radius=20,
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=10,
            color="#00000008",
            offset=ft.Offset(0, 4),
        ),
        content=ft.Column(items, spacing=14),
    )


def role_card(title, description, icon, on_click, accent):
    return ft.Container(
        padding=18,
        border_radius=RADIUS_MD,
        bgcolor="#FFFFFF",
        border=ft.Border.all(1, CARD_BORDER),
        content=ft.Column(
            [
                ft.Icon(icon, size=34, color=accent),
                ft.Text(title, size=18, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                ft.Text(description, size=13, color=TEXT_MUTED, text_align=ft.TextAlign.CENTER),
                ft.Container(height=6),
                ft.Button(
                    f"Continue as {title}",
                    on_click=on_click,
                    width=AUTH_BUTTON_WIDTH,
                    height=44,
                    style=ft.ButtonStyle(
                        bgcolor=accent,
                        color=BUTTON_TEXT,
                        shape=ft.RoundedRectangleBorder(radius=RADIUS_SM),
                    ),
                ),
            ],
            spacing=10,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )


def status_chip(text, color=INFO):
    return ft.Container(
        padding=ft.Padding.symmetric(horizontal=10, vertical=6),
        bgcolor=f"{color}1A",
        border_radius=999,
        content=ft.Text(text, size=12, color=color, weight=ft.FontWeight.W_500),
    )


def empty_state(message, icon=ft.Icons.INFO_OUTLINE):
    return ft.Container(
        padding=20,
        border_radius=16,
        bgcolor="#FFFFFF",
        border=ft.Border.all(1, CARD_BORDER),
        content=ft.Column(
            [
                ft.Icon(icon, size=34, color=TEXT_MUTED),
                ft.Text(message, color=TEXT_MUTED, text_align=ft.TextAlign.CENTER),
            ],
            spacing=10,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )


def show_message(page, msg, color="green"):
    page.snack_bar = ft.SnackBar(
        ft.Text(msg, color="white"),
        bgcolor=color,
        behavior=ft.SnackBarBehavior.FLOATING,
    )
    page.snack_bar.open = True
    page.update()


def show_success(page, msg):
    show_message(page, msg, SUCCESS)


def show_error(page, msg):
    show_message(page, msg, DANGER)


def clear_page(page):
    page.controls.clear()
