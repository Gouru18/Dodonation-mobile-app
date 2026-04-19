import asyncio
import os
import webbrowser
from datetime import datetime

import flet as ft

from services.admin_service import AdminService
from services.auth_service import AuthService
from utils.constants import BUTTON_TEXT
from utils.helpers import show_message


def admin_panel_view(page: ft.Page):
    user = AuthService.user or {}
    if not (user.get("role") == "admin" or user.get("is_staff") or user.get("is_superuser")):
        return ft.View(
            route="/admin-panel",
            controls=[ft.Container(padding=24, content=ft.Text("Admin account required."))],
        )

    colors = {
        "bg": "#111111",
        "panel": "#232323",
        "panel_alt": "#2B2B2B",
        "header": "#4D819C",
        "header_dark": "#234055",
        "border": "#373737",
        "text": "#F2F2F2",
        "muted": "#BBC6CF",
        "link": "#77C7FF",
        "green": "#79C534",
        "yellow": "#E4C74B",
        "danger": "#D15050",
        "success": "#137333",
    }

    section_meta = {
        "home": {"title": "Site administration", "group": None, "sidebar": False},
        "users": {"title": "Users", "group": "Accounts", "sidebar": True, "add_label": "ADD USER"},
        "claims": {"title": "Claim requests", "group": "Donations", "sidebar": True, "add_label": None},
        "donations": {"title": "Donations", "group": "Donations", "sidebar": True, "add_label": "ADD DONATION"},
        "meetings": {"title": "Meetings", "group": "Meetings", "sidebar": True, "add_label": "ADD MEETING"},
        "donor_profiles": {"title": "Donor profiles", "group": "Profiles", "sidebar": True, "add_label": "ADD DONOR PROFILE"},
        "ngo_profiles": {"title": "Ngo profiles", "group": "Profiles", "sidebar": True, "add_label": "ADD NGO PROFILE"},
        "permits": {"title": "Ngo permit applications", "group": "Profiles", "sidebar": True, "add_label": None},
    }

    sidebar_groups = [
        ("Accounts", [("users", "Users")]),
        ("Donations", [("claims", "Claim requests"), ("donations", "Donations")]),
        ("Meetings", [("meetings", "Meetings")]),
        ("Profiles", [("donor_profiles", "Donor profiles"), ("permits", "Ngo permit applications"), ("ngo_profiles", "Ngo profiles")]),
    ]

    state = {
        "section": "home",
        "dashboard": {},
        "recent_actions": [],
        "users": [],
        "claims": [],
        "donations": [],
        "meetings": [],
        "donor_profiles": [],
        "ngo_profiles": [],
        "permits": [],
        "selected_user_ids": set(),
        "user_role_filter": "all",
        "user_active_filter": "all",
        "user_email_filter": "all",
        "permit_status_filter": "all",
        "selected_user": None,
        "selected_claim": None,
        "selected_donation": None,
        "selected_meeting": None,
        "selected_donor_profile": None,
        "selected_ngo_profile": None,
        "selected_permit": None,
    }

    root_host = ft.Container(expand=True, bgcolor=colors["bg"])

    def admin_text(value, size=14, color=None, weight=None):
        return ft.Text(value, size=size, color=color or colors["text"], weight=weight)

    def nav_button(label, on_click):
        return ft.TextButton(label, on_click=on_click, style=ft.ButtonStyle(color=colors["text"]))

    def page_button(label, on_click, bgcolor="#4D819C", color=BUTTON_TEXT, width=None):
        return ft.Button(label, on_click=on_click, bgcolor=bgcolor, color=color, width=width)

    def text_link(label, on_click, color=None):
        return ft.TextButton(label, on_click=on_click, style=ft.ButtonStyle(color=color or colors["link"]))

    def input_field(label="", value=""):
        return ft.TextField(
            label=label,
            value=value,
            color=colors["text"],
            border_color=colors["border"],
            bgcolor="#161616",
            focused_border_color=colors["link"],
        )

    def multiline_field(label="", value="", lines=5):
        return ft.TextField(
            label=label,
            value=value,
            multiline=True,
            min_lines=lines,
            max_lines=max(lines + 2, lines),
            color=colors["text"],
            border_color=colors["border"],
            bgcolor="#161616",
            focused_border_color=colors["link"],
        )

    def dropdown_field(label, options, value=None, width=280):
        return ft.Dropdown(
            label=label,
            value=value,
            options=[ft.dropdown.Option(item, item.replace("_", " ").title()) for item in options],
            color=colors["text"],
            border_color=colors["border"],
            bgcolor="#161616",
            focused_border_color=colors["link"],
            width=width,
        )

    def panel(content, padding=16, bgcolor=None, expand=False, width=None):
        return ft.Container(
            content=content,
            padding=padding,
            bgcolor=bgcolor or colors["panel"],
            border=ft.Border.all(1, colors["border"]),
            expand=expand,
            width=width,
        )

    def bool_badge(value):
        if value:
            return ft.Icon(ft.Icons.CHECK_CIRCLE, color=colors["green"], size=18)
        return admin_text("-", color=colors["muted"])

    def clean_value(value, fallback="-"):
        if value is None or value == "":
            return fallback
        return str(value)

    def format_dt(value):
        if not value:
            return "-"
        text = str(value)
        try:
            return datetime.fromisoformat(text.replace("Z", "+00:00")).strftime("%b %d, %Y %I:%M %p")
        except ValueError:
            return text.replace("T", " ")

    def parse_int_value(value, label):
        if value in (None, ""):
            raise ValueError(f"{label} is required.")
        try:
            return int(str(value).strip())
        except ValueError as exc:
            raise ValueError(f"{label} must be a number.") from exc

    def parse_optional_float(value, label):
        if value in (None, ""):
            return None
        try:
            return float(str(value).strip())
        except ValueError as exc:
            raise ValueError(f"{label} must be a decimal number.") from exc

    def find_user_by_username(username):
        name = (username or "").strip().lower()
        for item in state["users"]:
            if (item.get("username") or "").strip().lower() == name:
                return item
        return None

    def find_ngo_profile_by_username(username):
        name = (username or "").strip().lower()
        for item in state["ngo_profiles"]:
            user_info = item.get("user") or {}
            if (user_info.get("username") or "").strip().lower() == name:
                return item
        return None

    def refresh_user_dropdowns():
        donor_names = sorted([(item.get("username") or "") for item in state["users"] if (item.get("role") or "") == "donor"])
        ngo_names = sorted([(item.get("username") or "") for item in state["users"] if (item.get("role") or "") == "ngo"])
        all_names = sorted([(item.get("username") or "") for item in state["users"] if item.get("username")])

        user_role.options = [ft.dropdown.Option(name, name.title()) for name in ["donor", "ngo", "admin"]]
        meeting_status.options = [ft.dropdown.Option(name, name.replace("_", " ").title()) for name in ["online_scheduled", "online_completed", "location_pinned", "physical_completed", "cancelled"]]
        donation_category.options = [ft.dropdown.Option(name, name.title()) for name in ["food", "clothing", "medical", "books", "furniture", "electronics", "other"]]
        donation_status.options = [ft.dropdown.Option(name, name.title()) for name in ["available", "pending", "claimed", "expired"]]

    def permit_state_label(permit):
        if not permit:
            return "not submitted"
        if permit.get("reviewed_at") or permit.get("status") in {"approved", "rejected"}:
            return "reviewed"
        if permit.get("submitted_at"):
            return "submitted"
        return clean_value(permit.get("status"))

    def response_message(response):
        try:
            data = response.json()
            if isinstance(data, dict):
                if data.get("message"):
                    return str(data["message"])
                if data.get("detail"):
                    return str(data["detail"])
                if data.get("error"):
                    return str(data["error"])
                for value in data.values():
                    if isinstance(value, list) and value:
                        return str(value[0])
            return response.text
        except Exception:
            return response.text

    async def run_request(request_fn, success_message="", refresh_fn=None):
        response = await asyncio.to_thread(request_fn)
        if response.status_code in (200, 201, 204):
            if success_message:
                state["recent_actions"] = [success_message] + state["recent_actions"][:7]
                show_message(page, success_message, colors["success"])
            if refresh_fn is not None:
                await refresh_fn()
            return response
        show_message(page, response_message(response), "red")
        return response

    def set_section(section_name):
        state["section"] = section_name
        render()
        page.update()

    async def logout(_=None):
        AuthService.logout()
        await page.push_route("/")

    def sidebar_item(key, label):
        is_active = state["section"] == key
        row_bg = "#0B4D57" if is_active else colors["panel"]
        return ft.Container(
            bgcolor=row_bg,
            border=ft.Border(bottom=ft.BorderSide(1, colors["border"])),
            padding=ft.Padding.only(left=16, right=10, top=10, bottom=10),
            content=ft.Row(
                [
                    ft.Container(
                        expand=True,
                        content=text_link(label, lambda e, key=key: set_section(key)),
                    ),
                    text_link("Add", lambda e, key=key: open_create_mode(key), color=colors["green"]) if section_meta[key].get("add_label") else admin_text(""),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

    def build_sidebar():
        groups = [input_field("", "")]
        groups[0].hint_text = "Start typing to filter..."
        groups[0].disabled = True
        groups[0].label = None
        groups[0].content_padding = 10

        for title, items in sidebar_groups:
            groups.append(
                ft.Container(
                    bgcolor=colors["header"],
                    padding=12,
                    content=admin_text(title.upper(), weight=ft.FontWeight.W_600),
                )
            )
            for key, label in items:
                groups.append(sidebar_item(key, label))

        return ft.Container(
            width=345,
            bgcolor="#161616",
            border=ft.Border(right=ft.BorderSide(1, colors["border"])),
            content=ft.Column(groups, spacing=0, scroll=ft.ScrollMode.AUTO),
        )

    def build_breadcrumb():
        if state["section"] == "home":
            return ft.Container(height=0)
        meta = section_meta[state["section"]]
        breadcrumb = ft.Row(
            [
                text_link("Home", lambda e: set_section("home")),
                admin_text("›", size=20, color=colors["muted"]),
                text_link(meta["group"], lambda e, section=state["section"]: set_section(section)),
                admin_text("›", size=20, color=colors["muted"]),
                admin_text(meta["title"], color=colors["text"]),
            ],
            spacing=6,
        )
        return ft.Container(bgcolor=colors["header_dark"], padding=ft.Padding.only(left=24, right=24, top=12, bottom=12), content=breadcrumb)

    def build_shell(main_content):
        show_sidebar = section_meta[state["section"]]["sidebar"]
        body = ft.Row(
            [
                build_sidebar() if show_sidebar else ft.Container(width=0),
                ft.Container(
                    expand=True,
                    padding=24,
                    content=ft.Column([main_content], expand=True, scroll=ft.ScrollMode.AUTO),
                ),
            ],
            expand=True,
            spacing=0,
        )
        return ft.Container(
            expand=True,
            bgcolor=colors["bg"],
            content=ft.Column(
                [
                    ft.Container(
                        bgcolor=colors["header"],
                        padding=ft.Padding.only(left=18, right=18, top=16, bottom=16),
                        content=ft.Row(
                            [
                                admin_text("Django administration", size=24, color="#F2D24A"),
                                ft.Row(
                                    [
                                        nav_button("WELCOME, ADMIN.", lambda e: None),
                                        nav_button("VIEW SITE", lambda e: set_section("home")),
                                        nav_button("CHANGE PASSWORD", lambda e: set_section("home")),
                                        nav_button("LOG OUT", lambda e: page.run_task(logout)),
                                    ],
                                    spacing=4,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                    ),
                    build_breadcrumb(),
                    ft.Container(expand=True, content=body),
                ],
                spacing=0,
                expand=True,
            ),
        )

    def module_row(label, section_name):
        add_label = section_meta[section_name].get("add_label")
        return ft.Container(
            bgcolor=colors["panel"],
            border=ft.Border(bottom=ft.BorderSide(1, colors["border"])),
            padding=12,
            content=ft.Row(
                [
                    ft.Container(expand=True, content=text_link(label, lambda e, section_name=section_name: set_section(section_name))),
                    ft.Row(
                        [
                            text_link("Add", lambda e, section_name=section_name: open_create_mode(section_name), color=colors["green"]) if add_label else admin_text(""),
                            text_link("Change", lambda e, section_name=section_name: set_section(section_name), color=colors["yellow"]),
                        ],
                        spacing=10,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        )

    def stat_box(number, label, detail=""):
        controls = [admin_text(str(number), size=26, color="#E8EDF2", weight=ft.FontWeight.BOLD), admin_text(label)]
        if detail:
            controls.append(admin_text(detail, size=12, color=colors["muted"]))
        return panel(ft.Column(controls, spacing=4), width=150, padding=14)

    def home_page():
        dashboard = state["dashboard"] or {}
        user_stats = dashboard.get("users", {})
        permit_stats = dashboard.get("permits", {})
        donation_stats = dashboard.get("donations", {})
        claim_stats = dashboard.get("claims", {})
        actions = state["recent_actions"][:5] or [
            f"Users: {user_stats.get('total', 0)} total",
            f"Submitted permits: {permit_stats.get('pending', 0)}",
            f"Donations: {donation_stats.get('total', 0)} total",
            f"Claims: {claim_stats.get('pending', 0)} pending",
        ]

        left = ft.Column(
            [
                admin_text("Site administration", size=28),
                ft.Container(height=8),
                ft.Column(
                    [
                        ft.Container(bgcolor=colors["header"], padding=12, content=admin_text("ACCOUNTS", weight=ft.FontWeight.W_600)),
                        module_row("Users", "users"),
                    ],
                    spacing=0,
                ),
                ft.Column(
                    [
                        ft.Container(bgcolor=colors["header"], padding=12, content=admin_text("DONATIONS", weight=ft.FontWeight.W_600)),
                        module_row("Claim requests", "claims"),
                        module_row("Donations", "donations"),
                    ],
                    spacing=0,
                ),
                ft.Column(
                    [
                        ft.Container(bgcolor=colors["header"], padding=12, content=admin_text("MEETINGS", weight=ft.FontWeight.W_600)),
                        module_row("Meetings", "meetings"),
                    ],
                    spacing=0,
                ),
                ft.Column(
                    [
                        ft.Container(bgcolor=colors["header"], padding=12, content=admin_text("PROFILES", weight=ft.FontWeight.W_600)),
                        module_row("Donor profiles", "donor_profiles"),
                        module_row("Ngo permit applications", "permits"),
                        module_row("Ngo profiles", "ngo_profiles"),
                    ],
                    spacing=0,
                ),
            ],
            spacing=18,
            expand=True,
        )
        right = panel(
            ft.Column(
                [
                    admin_text("Recent actions", size=18),
                    ft.Divider(color=colors["border"]),
                    admin_text("My actions", size=16, weight=ft.FontWeight.BOLD),
                    *[
                        ft.Container(
                            border=ft.Border(bottom=ft.BorderSide(1, colors["border"])),
                            padding=ft.Padding.only(top=8, bottom=8),
                            content=ft.Column(
                                [
                                    admin_text(item, size=13, color=colors["link"]),
                                    admin_text("Admin action", size=11, color=colors["muted"]),
                                ],
                                spacing=2,
                            ),
                        )
                        for item in actions
                    ],
                    ft.Divider(color=colors["border"]),
                    ft.Row(
                        [
                            stat_box(user_stats.get("total", 0), "Users", f"Admins: {user_stats.get('admins', 0)}"),
                            stat_box(user_stats.get("ngos", 0), "NGOs", f"Donors: {user_stats.get('donors', 0)}"),
                        ],
                        spacing=12,
                    ),
                    ft.Row(
                        [
                            stat_box(permit_stats.get("pending", 0), "Submitted permits"),
                            stat_box(donation_stats.get("total", 0), "Donations", f"Claimed: {donation_stats.get('claimed', 0)}"),
                        ],
                        spacing=12,
                    ),
                    ft.Row(
                        [
                            stat_box(claim_stats.get("pending", 0), "Pending claims"),
                            stat_box(dashboard.get("meetings", {}).get("total", 0), "Meetings", f"Active: {dashboard.get('meetings', {}).get('active', 0)}"),
                        ],
                        spacing=12,
                    ),
                ],
                spacing=10,
            ),
            width=360,
        )
        return ft.Row([ft.Container(expand=True, content=left), right], spacing=28, vertical_alignment=ft.CrossAxisAlignment.START)

    def build_table(headers, rows):
        return ft.Column(
            [
                ft.Container(
                    bgcolor=colors["panel_alt"],
                    padding=10,
                    content=ft.Row(headers, spacing=0, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ),
                ft.Column(rows or [ft.Container(padding=14, content=admin_text("No records found.", color=colors["muted"]))], spacing=0),
            ],
            spacing=0,
        )

    def table_cell(label, width, align_right=False, control=None, color=None):
        content = control or admin_text(label, size=13, color=color)
        alignment = ft.Alignment(1, 0) if align_right else ft.Alignment(-1, 0)
        return ft.Container(width=width, alignment=alignment, padding=ft.Padding.only(left=10, right=10), content=content)

    def table_row(cells, active=False):
        return ft.Container(
            bgcolor="#0A4955" if active else colors["panel"],
            border=ft.Border(bottom=ft.BorderSide(1, colors["border"])),
            padding=10,
            content=ft.Row(cells, spacing=0, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        )

    def search_bar(search_field, on_search):
        return ft.Container(
            bgcolor=colors["panel"],
            padding=12,
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.SEARCH, color=colors["muted"]),
                    ft.Container(expand=True, content=search_field),
                    page_button("Search", on_search, bgcolor="#151515"),
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

    def info_line(text):
        return admin_text(text, size=13, color=colors["text"])

    def filter_panel(title, sections):
        controls = [admin_text(title, size=18), ft.Divider(color=colors["border"])]
        for section_title, links in sections:
            controls.append(admin_text(section_title, size=14, weight=ft.FontWeight.BOLD))
            for label, active, handler in links:
                controls.append(text_link(label, handler, color=colors["link"] if active else colors["muted"]))
            controls.append(ft.Container(height=10))
        return panel(ft.Column(controls, spacing=6), width=300, padding=16)

    def field_row(label, control, help_text=""):
        controls = [
            ft.Container(width=220, content=admin_text(label, size=15, weight=ft.FontWeight.BOLD)),
            ft.Container(expand=True, content=control),
        ]
        if help_text:
            controls.append(ft.Container(width=220))
            controls.append(ft.Container(expand=True, content=admin_text(help_text, size=12, color=colors["muted"])))
        return ft.Column(
            [
                ft.Row(controls[:2], spacing=10, vertical_alignment=ft.CrossAxisAlignment.START),
                ft.Container(height=6),
                ft.Divider(color=colors["border"]),
            ],
            spacing=0,
        )

    def checkbox_with_label(checkbox, label):
        return ft.Row(
            [
                checkbox,
                admin_text(label, size=14),
            ],
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def editor_panel(title, rows, save_handler=None, delete_handler=None, clear_handler=None):
        buttons = []
        if save_handler is not None:
            buttons.extend(
                [
                    page_button("SAVE", lambda e: page.run_task(save_handler), bgcolor=colors["header"]),
                    page_button("Save and add another", lambda e: page.run_task(save_and_add_another, save_handler, clear_handler), bgcolor=colors["header"]),
                    page_button("Save and continue editing", lambda e: page.run_task(save_handler), bgcolor=colors["header"]),
                ]
            )
        if delete_handler is not None:
            buttons.append(page_button("DELETE", lambda e: page.run_task(delete_handler), bgcolor=colors["danger"]))
        return ft.Column(
            [
                admin_text(title, size=26),
                panel(
                    ft.Column(
                        rows
                        + [
                            ft.Container(
                                bgcolor=colors["panel"],
                                padding=12,
                                content=ft.Row(buttons, spacing=12),
                            )
                        ],
                        spacing=0,
                    ),
                    padding=0,
                    bgcolor=colors["bg"],
                ),
            ],
            spacing=16,
        )

    async def save_and_add_another(save_handler, clear_handler):
        result = await save_handler()
        if result and clear_handler is not None:
            clear_handler()
            render()
            page.update()

    def changelist_page(title, count_text, add_label, add_handler, search_control, search_handler, body, filter_content=None, editor=None):
        heading_controls = [admin_text(f"Select {title[:-1] if title.endswith('s') else title} to change", size=28)]
        action_row = ft.Row([], spacing=8)
        content_controls = [
            ft.Row(
                [
                    ft.Container(expand=True, content=ft.Column(heading_controls, spacing=4)),
                    page_button(add_label, add_handler, bgcolor="#3C3C3C") if add_label else ft.Container(),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            search_bar(search_control, search_handler),
        ]
        if action_row.controls:
            content_controls.append(action_row)
        content_controls.append(
            ft.Row(
                [
                    ft.Container(expand=True, content=body),
                    filter_content if filter_content is not None else ft.Container(width=0),
                ],
                spacing=24,
                vertical_alignment=ft.CrossAxisAlignment.START,
            )
        )
        content_controls.append(info_line(count_text))
        if editor is not None:
            content_controls.append(ft.Container(height=10))
            content_controls.append(editor)
        return ft.Column(content_controls, spacing=18)

    async def load_dashboard():
        response = await asyncio.to_thread(AdminService.get_dashboard)
        if response.status_code == 200:
            state["dashboard"] = response.json()
            render()
            page.update()

    user_search = input_field()
    user_search.hint_text = "Search by username or email"
    user_bulk_action = dropdown_field("", ["", "activate", "suspend", "delete"], "")
    user_bulk_action.label = None
    user_username = input_field("Username")
    user_email = input_field("Email")
    user_password = input_field("Password")
    user_password.password = True
    user_password.can_reveal_password = True
    user_role = dropdown_field("Role", ["donor", "ngo", "admin"], "donor")
    user_phone = input_field("Phone")
    user_active = ft.Checkbox(label="", value=True)
    user_staff = ft.Checkbox(label="", value=False)
    user_superuser = ft.Checkbox(label="", value=False)
    user_email_verified = ft.Checkbox(label="", value=False)
    user_phone_verified = ft.Checkbox(label="", value=False)

    def clear_user_form():
        state["selected_user"] = None
        user_username.value = ""
        user_email.value = ""
        user_password.value = ""
        user_role.value = "donor"
        user_phone.value = ""
        user_active.value = True
        user_staff.value = False
        user_superuser.value = False
        user_email_verified.value = False
        user_phone_verified.value = False

    def load_user_form(item):
        state["selected_user"] = item
        user_username.value = item.get("username") or ""
        user_email.value = item.get("email") or ""
        user_password.value = ""
        user_role.value = item.get("role") or "donor"
        user_phone.value = item.get("phone") or ""
        user_active.value = bool(item.get("is_active"))
        user_staff.value = bool(item.get("is_staff"))
        user_superuser.value = bool(item.get("is_superuser"))
        user_email_verified.value = bool(item.get("is_email_verified"))
        user_phone_verified.value = bool(item.get("is_phone_verified"))

    async def load_users():
        response = await asyncio.to_thread(AdminService.list_users, user_search.value or "")
        if response.status_code == 200:
            state["users"] = response.json()
            state["selected_user_ids"] = set()
            refresh_user_dropdowns()
            render()
            page.update()

    def filtered_users():
        items = list(state["users"])
        if state["user_role_filter"] != "all":
            items = [item for item in items if (item.get("role") or "") == state["user_role_filter"]]
        if state["user_active_filter"] == "yes":
            items = [item for item in items if item.get("is_active")]
        elif state["user_active_filter"] == "no":
            items = [item for item in items if not item.get("is_active")]
        if state["user_email_filter"] == "yes":
            items = [item for item in items if item.get("is_email_verified")]
        elif state["user_email_filter"] == "no":
            items = [item for item in items if not item.get("is_email_verified")]
        return items

    async def save_user():
        try:
            payload = {
                "username": user_username.value,
                "email": user_email.value,
                "role": user_role.value,
                "phone": user_phone.value,
                "is_active": bool(user_active.value),
                "is_staff": bool(user_staff.value),
                "is_superuser": bool(user_superuser.value),
                "is_email_verified": bool(user_email_verified.value),
                "is_phone_verified": bool(user_phone_verified.value),
            }
            if user_password.value:
                payload["password"] = user_password.value
            selected = state["selected_user"] or {}
            response = await run_request(lambda: AdminService.save_user(selected.get("id"), payload), "User saved.", load_users)
            if response.status_code in (200, 201):
                data = response.json()
                load_user_form(data)
                render()
                page.update()
                return True
        except Exception as exc:
            show_message(page, str(exc), "red")
        return False

    async def delete_user():
        selected = state["selected_user"] or {}
        if not selected.get("id"):
            show_message(page, "Select a user first.", "red")
            return
        await run_request(lambda: AdminService.delete_user(selected["id"]), "User deleted.", load_users)
        clear_user_form()
        render()
        page.update()

    async def activate_user():
        selected = state["selected_user"] or {}
        if not selected.get("id"):
            show_message(page, "Select a user first.", "red")
            return
        await run_request(lambda: AdminService.activate_user(selected["id"]), "User activated.", load_users)

    async def suspend_user():
        selected = state["selected_user"] or {}
        if not selected.get("id"):
            show_message(page, "Select a user first.", "red")
            return
        await run_request(lambda: AdminService.suspend_user(selected["id"]), "User suspended.", load_users)

    def toggle_user_selection(user_id, checked):
        selected_ids = set(state["selected_user_ids"])
        if checked:
            selected_ids.add(user_id)
        else:
            selected_ids.discard(user_id)
        state["selected_user_ids"] = selected_ids
        render()
        page.update()

    def toggle_all_users(checked):
        visible_ids = [item.get("id") for item in filtered_users()]
        state["selected_user_ids"] = set(visible_ids if checked else [])
        render()
        page.update()

    async def run_user_bulk_action():
        action = user_bulk_action.value or ""
        if not action:
            show_message(page, "Choose an action first.", "red")
            return
        if not state["selected_user_ids"]:
            show_message(page, "Select at least one user.", "red")
            return
        for user_id in list(state["selected_user_ids"]):
            if action == "activate":
                await asyncio.to_thread(AdminService.activate_user, user_id)
            elif action == "suspend":
                await asyncio.to_thread(AdminService.suspend_user, user_id)
            elif action == "delete":
                await asyncio.to_thread(AdminService.delete_user, user_id)
        state["selected_user_ids"] = set()
        user_bulk_action.value = ""
        show_message(page, "Bulk action completed.", colors["success"])
        await load_users()

    def set_bulk_action_and_run(action):
        user_bulk_action.value = action
        page.run_task(run_user_bulk_action)

    claim_search = input_field()
    claim_search.hint_text = "Search by donation title or NGO email"
    claim_receiver_username = input_field("NGO username")
    claim_status = dropdown_field("Status", ["pending", "accepted", "rejected"], "pending")
    claim_message = multiline_field("Message", "", 5)

    def clear_claim_form():
        state["selected_claim"] = None
        claim_receiver_username.value = ""
        claim_status.value = "pending"
        claim_message.value = ""

    def load_claim_form(item):
        state["selected_claim"] = item
        claim_receiver_username.value = (item.get("receiver") or {}).get("username") or ""
        claim_status.value = item.get("status") or "pending"
        claim_message.value = item.get("message") or ""

    async def load_claims():
        response = await asyncio.to_thread(AdminService.list_claims, claim_search.value or "")
        if response.status_code == 200:
            state["claims"] = response.json()
            render()
            page.update()

    async def save_claim():
        try:
            selected = state["selected_claim"] or {}
            if not selected.get("id"):
                show_message(page, "Select an existing claim request to edit.", "red")
                return False
            receiver = find_user_by_username(claim_receiver_username.value)
            if not receiver:
                show_message(page, "Enter an existing NGO username.", "red")
                return False
            donation = selected.get("donation") or {}
            donation_id = donation.get("id")
            if not donation_id:
                show_message(page, "This claim request is missing its donation reference.", "red")
                return False
            payload = {
                "donation_id": donation_id,
                "receiver_id": receiver["id"],
                "status": claim_status.value,
                "message": claim_message.value,
            }
            response = await run_request(lambda: AdminService.save_claim(selected.get("id"), payload), "Claim request saved.", load_claims)
            if response.status_code in (200, 201):
                load_claim_form(response.json())
                render()
                page.update()
                return True
        except Exception as exc:
            show_message(page, str(exc), "red")
        return False

    async def delete_claim():
        selected = state["selected_claim"] or {}
        if not selected.get("id"):
            show_message(page, "Select a claim request first.", "red")
            return
        response = await run_request(lambda: AdminService.delete_claim(selected["id"]), "Claim request deleted.", load_claims)
        if response.status_code == 204:
            clear_claim_form()
            render()
            page.update()
        elif response.status_code == 404:
            clear_claim_form()
            await load_claims()
            show_message(page, "That claim request was already removed.", colors["warning"])

    donor_profile_search = input_field()
    donor_profile_search.hint_text = "Search by full name or email"
    donor_profile_username = input_field("Username")
    donor_profile_full_name = input_field("Full name")
    donor_profile_address = multiline_field("Address", "", 5)

    def clear_donor_profile_form():
        state["selected_donor_profile"] = None
        donor_profile_username.value = ""
        donor_profile_full_name.value = ""
        donor_profile_address.value = ""

    def load_donor_profile_form(item):
        state["selected_donor_profile"] = item
        donor_profile_username.value = (item.get("user") or {}).get("username") or ""
        donor_profile_full_name.value = item.get("full_name") or ""
        donor_profile_address.value = item.get("address") or ""

    async def load_donor_profiles():
        response = await asyncio.to_thread(AdminService.list_donor_profiles, donor_profile_search.value or "")
        if response.status_code == 200:
            state["donor_profiles"] = response.json()
            render()
            page.update()

    async def save_donor_profile():
        try:
            selected_user = find_user_by_username(donor_profile_username.value)
            if not selected_user:
                show_message(page, "Select an existing donor username.", "red")
                return False
            payload = {
                "user_id": selected_user["id"],
                "full_name": donor_profile_full_name.value,
                "address": donor_profile_address.value,
            }
            selected = state["selected_donor_profile"] or {}
            response = await run_request(lambda: AdminService.save_donor_profile(selected.get("id"), payload), "Donor profile saved.", load_donor_profiles)
            if response.status_code in (200, 201):
                load_donor_profile_form(response.json())
                render()
                page.update()
                return True
        except Exception as exc:
            show_message(page, str(exc), "red")
        return False

    async def delete_donor_profile():
        selected = state["selected_donor_profile"] or {}
        if not selected.get("id"):
            show_message(page, "Select a donor profile first.", "red")
            return
        await run_request(lambda: AdminService.delete_donor_profile(selected["id"]), "Donor profile deleted.", load_donor_profiles)
        clear_donor_profile_form()

    ngo_profile_search = input_field()
    ngo_profile_search.hint_text = "Search by organization or email"
    ngo_profile_username = input_field("Username")
    ngo_profile_organization = input_field("Organization name")
    ngo_profile_registration = input_field("Registration number")
    ngo_profile_address = multiline_field("Address", "", 5)

    def clear_ngo_profile_form():
        state["selected_ngo_profile"] = None
        ngo_profile_username.value = ""
        ngo_profile_organization.value = ""
        ngo_profile_registration.value = ""
        ngo_profile_address.value = ""

    def load_ngo_profile_form(item):
        state["selected_ngo_profile"] = item
        ngo_profile_username.value = (item.get("user") or {}).get("username") or ""
        ngo_profile_organization.value = item.get("organization_name") or ""
        ngo_profile_registration.value = item.get("registration_number") or ""
        ngo_profile_address.value = item.get("address") or ""

    async def load_ngo_profiles():
        response = await asyncio.to_thread(AdminService.list_ngo_profiles, ngo_profile_search.value or "")
        if response.status_code == 200:
            state["ngo_profiles"] = response.json()
            render()
            page.update()

    async def save_ngo_profile():
        try:
            selected_user = find_user_by_username(ngo_profile_username.value)
            if not selected_user:
                show_message(page, "Select an existing NGO username.", "red")
                return False
            payload = {
                "user_id": selected_user["id"],
                "organization_name": ngo_profile_organization.value,
                "registration_number": ngo_profile_registration.value,
                "address": ngo_profile_address.value,
            }
            selected = state["selected_ngo_profile"] or {}
            response = await run_request(lambda: AdminService.save_ngo_profile(selected.get("id"), payload), "NGO profile saved.", load_ngo_profiles)
            if response.status_code in (200, 201):
                load_ngo_profile_form(response.json())
                render()
                page.update()
                return True
        except Exception as exc:
            show_message(page, str(exc), "red")
        return False

    async def delete_ngo_profile():
        selected = state["selected_ngo_profile"] or {}
        if not selected.get("id"):
            show_message(page, "Select an NGO profile first.", "red")
            return
        await run_request(lambda: AdminService.delete_ngo_profile(selected["id"]), "NGO profile deleted.", load_ngo_profiles)
        clear_ngo_profile_form()

    permit_search = input_field()
    permit_search.hint_text = "Search by organization name"
    permit_username = input_field("NGO username")
    permit_rejection_reason = multiline_field("Rejection reason", "", 4)
    permit_file_path = input_field("Permit file path")

    def clear_permit_form():
        state["selected_permit"] = None
        permit_username.value = ""
        permit_rejection_reason.value = ""
        permit_file_path.value = ""

    def load_permit_form(item):
        state["selected_permit"] = item
        permit_username.value = (((item.get("ngo") or {}).get("user")) or {}).get("username") or ""
        permit_rejection_reason.value = item.get("rejection_reason") or ""
        permit_file_path.value = ""

    async def load_permits():
        filter_value = "" if state["permit_status_filter"] == "all" else state["permit_status_filter"]
        response = await asyncio.to_thread(AdminService.list_permits, permit_search.value or "", filter_value)
        if response.status_code == 200:
            state["permits"] = response.json()
            render()
            page.update()

    async def save_permit():
        try:
            selected = state["selected_permit"] or {}
            if not selected.get("id"):
                show_message(page, "Select an existing permit application first.", "red")
                return False
            response = await run_request(
                lambda: AdminService.save_permit(
                    selected.get("id"),
                    None,
                    (permit_file_path.value or "").strip() or None,
                    permit_rejection_reason.value or "",
                ),
                "Permit application updated.",
                load_permits,
            )
            if response.status_code in (200, 201):
                load_permit_form(response.json())
                render()
                page.update()
                return True
        except Exception as exc:
            show_message(page, str(exc), "red")
        return False

    async def approve_permit():
        selected = state["selected_permit"] or {}
        if not selected.get("id"):
            show_message(page, "Select a permit application first.", "red")
            return
        await run_request(lambda: AdminService.approve_permit(selected["id"]), "Permit approved.", load_permits)

    async def reject_permit():
        selected = state["selected_permit"] or {}
        if not selected.get("id"):
            show_message(page, "Select a permit application first.", "red")
            return
        await run_request(lambda: AdminService.reject_permit(selected["id"], permit_rejection_reason.value or ""), "Permit rejected.", load_permits)

    async def delete_permit():
        selected = state["selected_permit"] or {}
        if not selected.get("id"):
            show_message(page, "Select a permit application first.", "red")
            return
        await run_request(lambda: AdminService.delete_permit(selected["id"]), "Permit application deleted.", load_permits)
        clear_permit_form()

    donation_search = input_field()
    donation_search.hint_text = "Search by title or donor email"
    donation_donor_username = input_field("Donor username")
    donation_title = input_field("Title")
    donation_description = multiline_field("Description", "", 5)
    donation_category = dropdown_field("Category", ["food", "clothing", "medical", "books", "furniture", "electronics", "other"], "other")
    donation_quantity = input_field("Quantity")
    donation_expiry = input_field("Expiry date")
    donation_status = dropdown_field("Status", ["available", "pending", "claimed", "expired"], "available")
    donation_image_path = input_field("Image file path")

    def clear_donation_form():
        state["selected_donation"] = None
        donation_donor_username.value = ""
        donation_title.value = ""
        donation_description.value = ""
        donation_category.value = "other"
        donation_quantity.value = ""
        donation_expiry.value = ""
        donation_status.value = "available"
        donation_image_path.value = ""

    def load_donation_form(item):
        state["selected_donation"] = item
        donation_donor_username.value = (item.get("donor") or {}).get("username") or ""
        donation_title.value = item.get("title") or ""
        donation_description.value = item.get("description") or ""
        donation_category.value = item.get("category") or "other"
        donation_quantity.value = str(item.get("quantity") or "")
        donation_expiry.value = item.get("expiry_date") or ""
        donation_status.value = "available" if item.get("status") == "pending" else (item.get("status") or "available")
        donation_image_path.value = ""

    async def choose_donation_image():
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
                        ("Images", "*.png *.jpg *.jpeg *.gif *.webp"),
                        ("All files", "*.*"),
                    ],
                )
                root.destroy()
                return file_path
            except Exception:
                return None

        file_path = await asyncio.to_thread(choose_file)
        if file_path:
            donation_image_path.value = file_path
        page.update()

    async def load_donations():
        response = await asyncio.to_thread(AdminService.list_donations, donation_search.value or "")
        if response.status_code == 200:
            state["donations"] = response.json()
            render()
            page.update()

    async def save_donation():
        try:
            donor_user = find_user_by_username(donation_donor_username.value)
            if not donor_user:
                show_message(page, "Select an existing donor username.", "red")
                return False
            api_status = "pending" if donation_status.value == "available" else donation_status.value
            payload = {
                "donor_id": donor_user["id"],
                "title": donation_title.value,
                "description": donation_description.value,
                "category": donation_category.value,
                "quantity": parse_int_value(donation_quantity.value, "Quantity"),
                "expiry_date": donation_expiry.value or None,
                "status": api_status,
            }
            selected = state["selected_donation"] or {}
            image_path = (donation_image_path.value or "").strip() or None
            if image_path and not os.path.exists(image_path):
                show_message(page, "The selected image file was not found.", "red")
                return False
            if image_path:
                request_fn = lambda: AdminService.save_donation_with_image(selected.get("id"), payload, image_path)
            else:
                request_fn = lambda: AdminService.save_donation(selected.get("id"), payload)
            response = await run_request(request_fn, "Donation saved.", load_donations)
            if response.status_code in (200, 201):
                load_donation_form(response.json())
                render()
                page.update()
                return True
        except Exception as exc:
            show_message(page, str(exc), "red")
        return False

    async def delete_donation():
        selected = state["selected_donation"] or {}
        if not selected.get("id"):
            show_message(page, "Select a donation first.", "red")
            return
        await run_request(lambda: AdminService.delete_donation(selected["id"]), "Donation deleted.", load_donations)
        clear_donation_form()

    meeting_search = input_field()
    meeting_search.hint_text = "Search by donation title or participant email"
    meeting_scheduled_time = input_field("Scheduled time")
    meeting_link = input_field("Meeting link")
    meeting_address = input_field("Meeting address")
    meeting_status = dropdown_field("Status", ["online_scheduled", "online_completed", "location_pinned", "physical_completed", "cancelled"], "online_scheduled")

    def clear_meeting_form():
        state["selected_meeting"] = None
        meeting_scheduled_time.value = ""
        meeting_link.value = ""
        meeting_address.value = ""
        meeting_status.value = "online_scheduled"

    def load_meeting_form(item):
        state["selected_meeting"] = item
        meeting_scheduled_time.value = item.get("scheduled_time") or ""
        meeting_link.value = item.get("meeting_link") or ""
        meeting_address.value = item.get("meeting_address") or ""
        meeting_status.value = item.get("status") or "online_scheduled"

    def current_meeting_claim():
        selected_meeting = state["selected_meeting"] or {}
        meeting_claim = selected_meeting.get("claim_request") or {}
        if meeting_claim.get("id"):
            return meeting_claim
        selected_claim = state["selected_claim"] or {}
        if selected_claim.get("id"):
            return {
                "id": selected_claim.get("id"),
                "donation_title": ((selected_claim.get("donation") or {}).get("title")) or "",
                "receiver_email": ((selected_claim.get("receiver") or {}).get("email")) or "",
                "status": selected_claim.get("status") or "",
            }
        return {}

    async def load_meetings():
        response = await asyncio.to_thread(AdminService.list_meetings, meeting_search.value or "")
        if response.status_code == 200:
            state["meetings"] = response.json()
            render()
            page.update()

    async def save_meeting():
        try:
            selected = state["selected_meeting"] or {}
            meeting_claim = current_meeting_claim()
            claim_request_id = meeting_claim.get("id")
            if not claim_request_id:
                show_message(page, "Select a claim request first, then schedule the meeting.", "red")
                return False
            payload = {
                "claim_request_id": claim_request_id,
                "scheduled_time": meeting_scheduled_time.value,
                "meeting_link": meeting_link.value,
                "meeting_address": meeting_address.value,
                "status": meeting_status.value,
            }
            response = await run_request(lambda: AdminService.save_meeting(selected.get("id"), payload), "Meeting saved.", load_meetings)
            if response.status_code in (200, 201):
                load_meeting_form(response.json())
                render()
                page.update()
                return True
        except Exception as exc:
            show_message(page, str(exc), "red")
        return False

    async def delete_meeting():
        selected = state["selected_meeting"] or {}
        if not selected.get("id"):
            show_message(page, "Select a meeting first.", "red")
            return
        await run_request(lambda: AdminService.delete_meeting(selected["id"]), "Meeting deleted.", load_meetings)
        clear_meeting_form()

    def open_create_mode(section_name):
        state["section"] = section_name
        if section_name == "users":
            clear_user_form()
        elif section_name == "claims":
            clear_claim_form()
        elif section_name == "donor_profiles":
            clear_donor_profile_form()
        elif section_name == "ngo_profiles":
            clear_ngo_profile_form()
        elif section_name == "permits":
            clear_permit_form()
        elif section_name == "donations":
            clear_donation_form()
        elif section_name == "meetings":
            clear_meeting_form()
        render()
        page.update()

    def user_filter_handler(key, value):
        state[key] = value
        render()
        page.update()

    def open_url(url):
        if not url:
            show_message(page, "No file available.", "red")
            return
        try:
            opened = webbrowser.open(url)
            if not opened:
                page.launch_url(url)
        except Exception:
            page.launch_url(url)

    def users_page():
        items = filtered_users()
        header_row = ft.Row(
            [
                page_button("Activate selected", lambda e: set_bulk_action_and_run("activate"), bgcolor=colors["green"]),
                page_button("Suspend selected", lambda e: set_bulk_action_and_run("suspend"), bgcolor=colors["yellow"], color="#111111"),
                page_button("Delete selected", lambda e: set_bulk_action_and_run("delete"), bgcolor=colors["danger"]),
            ],
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        rows = []
        all_selected = bool(items) and all(item.get("id") in state["selected_user_ids"] for item in items)
        rows.append(
            ft.Container(
                bgcolor=colors["panel_alt"],
                padding=10,
                content=ft.Row(
                    [
                        ft.Container(
                            width=44,
                            content=ft.Checkbox(value=all_selected, on_change=lambda e: toggle_all_users(bool(e.control.value))),
                        ),
                        table_cell("USERNAME", 240),
                        table_cell("EMAIL ADDRESS", 290),
                        table_cell("ROLE", 120),
                        table_cell("ACTIVE", 110),
                        table_cell("PERMIT STATUS", 150),
                    ],
                    spacing=0,
                ),
            )
        )
        for item in items:
            permit = item.get("ngo_permit") or {}
            rows.append(
                ft.Container(
                    bgcolor="#0B4D57" if (state["selected_user"] or {}).get("id") == item.get("id") else colors["panel"],
                    border=ft.Border(bottom=ft.BorderSide(1, colors["border"])),
                    padding=10,
                    content=ft.Row(
                        [
                            ft.Container(
                                width=44,
                                content=ft.Checkbox(
                                    value=item.get("id") in state["selected_user_ids"],
                                    on_change=lambda e, user_id=item.get("id"): toggle_user_selection(user_id, bool(e.control.value)),
                                ),
                            ),
                            table_cell("", 240, control=text_link(clean_value(item.get("username")), lambda e, item=item: select_user(item))),
                            table_cell(clean_value(item.get("email")), 290),
                            table_cell(clean_value(item.get("role")), 120),
                            table_cell("", 110, control=bool_badge(item.get("is_active"))),
                            table_cell(permit_state_label(permit), 150),
                        ],
                        spacing=0,
                    ),
                )
            )

        filters = filter_panel(
            "FILTER",
            [
                (
                    "By role",
                    [
                        ("All", state["user_role_filter"] == "all", lambda e: user_filter_handler("user_role_filter", "all")),
                        ("Donor", state["user_role_filter"] == "donor", lambda e: user_filter_handler("user_role_filter", "donor")),
                        ("NGO", state["user_role_filter"] == "ngo", lambda e: user_filter_handler("user_role_filter", "ngo")),
                        ("Admin", state["user_role_filter"] == "admin", lambda e: user_filter_handler("user_role_filter", "admin")),
                    ],
                ),
                (
                    "By active",
                    [
                        ("All", state["user_active_filter"] == "all", lambda e: user_filter_handler("user_active_filter", "all")),
                        ("Yes", state["user_active_filter"] == "yes", lambda e: user_filter_handler("user_active_filter", "yes")),
                        ("No", state["user_active_filter"] == "no", lambda e: user_filter_handler("user_active_filter", "no")),
                    ],
                ),
                (
                    "By is email verified",
                    [
                        ("All", state["user_email_filter"] == "all", lambda e: user_filter_handler("user_email_filter", "all")),
                        ("Yes", state["user_email_filter"] == "yes", lambda e: user_filter_handler("user_email_filter", "yes")),
                        ("No", state["user_email_filter"] == "no", lambda e: user_filter_handler("user_email_filter", "no")),
                    ],
                ),
            ],
        )

        selected = state["selected_user"] or {}
        editor = editor_panel(
            f"{'Change' if selected.get('id') else 'Add'} user",
            [
                field_row("Username:", user_username),
                field_row("Email:", user_email),
                field_row("Password:", user_password),
                field_row("Role:", user_role),
                field_row("Phone:", user_phone),
                field_row(
                    "Status:",
                    ft.Container(
                        bgcolor="#1B1B1B",
                        border=ft.Border.all(1, colors["border"]),
                        padding=12,
                        content=ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Container(bgcolor=colors["green"] if user_active.value else colors["danger"], padding=ft.Padding.only(left=10, right=10, top=6, bottom=6), content=admin_text("ACTIVE" if user_active.value else "INACTIVE", weight=ft.FontWeight.BOLD)),
                                        ft.Container(bgcolor=colors["header"] if user_email_verified.value else colors["panel_alt"], padding=ft.Padding.only(left=10, right=10, top=6, bottom=6), content=admin_text("EMAIL VERIFIED" if user_email_verified.value else "EMAIL UNVERIFIED", weight=ft.FontWeight.BOLD)),
                                    ],
                                    spacing=10,
                                ),
                                ft.Column(
                                    [
                                        checkbox_with_label(user_active, "Active"),
                                        checkbox_with_label(user_staff, "Staff"),
                                        checkbox_with_label(user_superuser, "Superuser"),
                                        checkbox_with_label(user_email_verified, "Email verified"),
                                        checkbox_with_label(user_phone_verified, "Phone verified"),
                                    ],
                                    spacing=10,
                                ),
                            ],
                            spacing=12,
                        ),
                    ),
                ),
                field_row(
                    "Quick actions:",
                    ft.Row(
                        [
                            page_button("Activate", lambda e: page.run_task(activate_user), bgcolor=colors["green"]),
                            page_button("Suspend", lambda e: page.run_task(suspend_user), bgcolor=colors["yellow"], color="#111111"),
                        ],
                        spacing=12,
                    ),
                ),
            ],
            save_user,
            delete_user,
            clear_user_form,
        )

        return ft.Column(
            [
                admin_text("Select user to change", size=28),
                ft.Row([ft.Container(expand=True), page_button("ADD USER", lambda e: open_create_mode("users"), bgcolor="#3C3C3C")], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                search_bar(user_search, lambda e: page.run_task(load_users)),
                header_row,
                info_line(f"{len(state['selected_user_ids'])} of {len(items)} selected"),
                ft.Row(
                    [
                        ft.Container(expand=True, content=ft.Column([*rows, info_line(f"{len(items)} users")], spacing=10)),
                        filters,
                    ],
                    spacing=24,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
                editor,
            ],
            spacing=18,
        )

    def select_user(item):
        load_user_form(item)
        render()
        page.update()

    def simple_section_page(title, count_label, add_label, add_handler, search_control, search_handler, table_headers, table_rows, editor, filter_content=None):
        return ft.Column(
            [
                admin_text(f"Select {title[:-1] if title.endswith('s') else title} to change", size=28),
                ft.Row([ft.Container(expand=True), page_button(add_label, add_handler, bgcolor="#3C3C3C") if add_label else ft.Container()], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                search_bar(search_control, search_handler),
                ft.Row(
                    [
                        ft.Container(expand=True, content=build_table(table_headers, table_rows)),
                        filter_content if filter_content is not None else ft.Container(width=0),
                    ],
                    spacing=24,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
                info_line(count_label),
                editor,
            ],
            spacing=18,
        )

    def claims_page():
        rows = [
            table_row(
                [
                    table_cell("", 280, control=text_link(clean_value((item.get("donation") or {}).get("title")), lambda e, item=item: select_claim(item))),
                    table_cell(clean_value((item.get("receiver") or {}).get("email")), 280),
                    table_cell(clean_value(item.get("status")), 150),
                    table_cell(format_dt(item.get("date_requested")), 220),
                ],
                active=(state["selected_claim"] or {}).get("id") == item.get("id"),
            )
            for item in state["claims"]
        ]
        editor = editor_panel(
            "Change claim request",
            [
                field_row("Donation:", admin_text(clean_value(((state["selected_claim"] or {}).get("donation") or {}).get("title")))),
                field_row("NGO username:", claim_receiver_username),
                field_row("Status:", claim_status),
                field_row("Message:", claim_message),
            ],
            save_claim,
            delete_claim,
            clear_claim_form,
        )
        return simple_section_page(
            "Claim requests",
            f"{len(state['claims'])} claim requests",
            None,
            lambda e: None,
            claim_search,
            lambda e: page.run_task(load_claims),
            [table_cell("DONATION", 280), table_cell("NGO", 280), table_cell("STATUS", 150), table_cell("REQUESTED AT", 220)],
            rows,
            editor,
        )

    def select_claim(item):
        load_claim_form(item)
        render()
        page.update()

    def donor_profiles_page():
        rows = [
            table_row(
                [
                    table_cell("", 260, control=text_link(clean_value(item.get("full_name")), lambda e, item=item: select_donor_profile(item))),
                    table_cell(clean_value((item.get("user") or {}).get("email")), 280),
                    table_cell(clean_value(item.get("address"))[:80], 420),
                ],
                active=(state["selected_donor_profile"] or {}).get("id") == item.get("id"),
            )
            for item in state["donor_profiles"]
        ]
        editor = editor_panel(
            f"{'Change' if (state['selected_donor_profile'] or {}).get('id') else 'Add'} donor profile",
            [
                field_row("Username:", donor_profile_username),
                field_row("Full name:", donor_profile_full_name),
                field_row("Address:", donor_profile_address),
            ],
            save_donor_profile,
            delete_donor_profile,
            clear_donor_profile_form,
        )
        return simple_section_page(
            "Donor profiles",
            f"{len(state['donor_profiles'])} donor profiles",
            "ADD DONOR PROFILE",
            lambda e: open_create_mode("donor_profiles"),
            donor_profile_search,
            lambda e: page.run_task(load_donor_profiles),
            [table_cell("FULL NAME", 260), table_cell("EMAIL", 280), table_cell("ADDRESS", 420)],
            rows,
            editor,
        )

    def select_donor_profile(item):
        load_donor_profile_form(item)
        render()
        page.update()

    def ngo_profiles_page():
        rows = [
            table_row(
                [
                    table_cell("", 280, control=text_link(clean_value(item.get("organization_name")), lambda e, item=item: select_ngo_profile(item))),
                    table_cell(clean_value((item.get("user") or {}).get("email")), 260),
                    table_cell(clean_value(item.get("registration_number")), 180),
                    table_cell(permit_state_label(item.get("permit_application") or {}), 160),
                ],
                active=(state["selected_ngo_profile"] or {}).get("id") == item.get("id"),
            )
            for item in state["ngo_profiles"]
        ]
        editor = editor_panel(
            f"{'Change' if (state['selected_ngo_profile'] or {}).get('id') else 'Add'} ngo profile",
            [
                field_row("Username:", ngo_profile_username),
                field_row("Organization name:", ngo_profile_organization),
                field_row("Registration number:", ngo_profile_registration),
                field_row("Address:", ngo_profile_address),
            ],
            save_ngo_profile,
            delete_ngo_profile,
            clear_ngo_profile_form,
        )
        return simple_section_page(
            "Ngo profiles",
            f"{len(state['ngo_profiles'])} ngo profiles",
            "ADD NGO PROFILE",
            lambda e: open_create_mode("ngo_profiles"),
            ngo_profile_search,
            lambda e: page.run_task(load_ngo_profiles),
            [table_cell("ORGANIZATION", 280), table_cell("EMAIL", 260), table_cell("REGISTRATION NUMBER", 180), table_cell("PERMIT STATUS", 160)],
            rows,
            editor,
        )

    def select_ngo_profile(item):
        load_ngo_profile_form(item)
        render()
        page.update()

    def permits_page():
        rows = [
            table_row(
                [
                    table_cell("", 230, control=text_link(clean_value(((item.get("ngo") or {}).get("organization_name"))), lambda e, item=item: select_permit(item))),
                    table_cell(permit_state_label(item), 150),
                    table_cell(format_dt(item.get("submitted_at")), 220),
                    table_cell(clean_value(((item.get("reviewed_by") or {}).get("email"))), 220),
                    table_cell("", 220, control=text_link("Open uploaded permit", lambda e, url=item.get("permit_file_url"): open_url(url))),
                ],
                active=(state["selected_permit"] or {}).get("id") == item.get("id"),
            )
            for item in state["permits"]
        ]
        filters = filter_panel(
            "FILTER",
            [
                (
                    "By status",
                    [
                        ("All", state["permit_status_filter"] == "all", lambda e: set_permit_status_filter("all")),
                        ("Pending", state["permit_status_filter"] == "pending", lambda e: set_permit_status_filter("pending")),
                        ("Approved", state["permit_status_filter"] == "approved", lambda e: set_permit_status_filter("approved")),
                        ("Rejected", state["permit_status_filter"] == "rejected", lambda e: set_permit_status_filter("rejected")),
                    ],
                ),
            ],
        )
        selected = state["selected_permit"] or {}
        editor = editor_panel(
            f"{'Review' if selected.get('id') else 'Permit'} application",
            [
                field_row("Username:", permit_username),
                field_row("Ngo:", admin_text(clean_value(((selected.get("ngo") or {}).get("organization_name"))))),
                field_row(
                    "Status:",
                    ft.Container(
                        bgcolor=colors["green"] if permit_state_label(selected) == "reviewed" else colors["header"],
                        padding=ft.Padding.only(left=12, right=12, top=8, bottom=8),
                        content=admin_text(permit_state_label(selected).upper(), weight=ft.FontWeight.BOLD),
                    ),
                ),
                field_row("Submitted at:", admin_text(format_dt(selected.get("submitted_at")))),
                field_row("Reviewed by:", admin_text(clean_value(((selected.get("reviewed_by") or {}).get("email"))))),
                field_row("Rejection reason:", permit_rejection_reason),
                field_row("Permit file path:", permit_file_path, "Optional: replace the uploaded permit file for the selected application only."),
                field_row("Current file:", text_link("Open uploaded permit", lambda e, url=selected.get("permit_file_url"): open_url(url)) if selected.get("permit_file_url") else admin_text("No uploaded permit", color=colors["muted"])),
                field_row(
                    "Review actions:",
                    ft.Row(
                        [
                            page_button("SAVE", lambda e: page.run_task(save_permit), bgcolor=colors["header"]),
                            page_button("APPROVE", lambda e: page.run_task(approve_permit), bgcolor=colors["green"]),
                            page_button("REJECT", lambda e: page.run_task(reject_permit), bgcolor=colors["yellow"], color="#111111"),
                        ],
                        spacing=12,
                    ),
                ),
            ],
            None,
            delete_permit,
            clear_permit_form,
        )
        return ft.Column(
            [
                admin_text("Select ngo permit application to change", size=28),
                search_bar(permit_search, lambda e: page.run_task(load_permits)),
                ft.Row(
                    [
                        ft.Container(
                            expand=True,
                            content=ft.Column(
                                [
                                    build_table(
                                        [table_cell("NGO", 230), table_cell("STATUS", 150), table_cell("SUBMITTED AT", 220), table_cell("REVIEWED BY", 220), table_cell("PERMIT FILE", 220)],
                                        rows,
                                    ),
                                    info_line(f"{len(state['permits'])} ngo permit applications"),
                                ],
                                spacing=12,
                            ),
                        ),
                        filters,
                    ],
                    spacing=24,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
                editor,
            ],
            spacing=18,
        )

    def set_permit_status_filter(value):
        state["permit_status_filter"] = value
        page.run_task(load_permits)

    def select_permit(item):
        load_permit_form(item)
        render()
        page.update()

    def donations_page():
        rows = [
            table_row(
                [
                    table_cell("", 260, control=text_link(clean_value(item.get("title")), lambda e, item=item: select_donation(item))),
                    table_cell(clean_value((item.get("donor") or {}).get("email")), 280),
                    table_cell(clean_value(item.get("category")), 140),
                    table_cell(clean_value(item.get("status")), 140),
                    table_cell(clean_value(item.get("quantity")), 120),
                ],
                active=(state["selected_donation"] or {}).get("id") == item.get("id"),
            )
            for item in state["donations"]
        ]
        editor = editor_panel(
            f"{'Change' if (state['selected_donation'] or {}).get('id') else 'Add'} donation",
            [
                field_row("Donor username:", donation_donor_username),
                field_row("Title:", donation_title),
                field_row("Description:", donation_description),
                field_row("Category:", donation_category),
                field_row("Quantity:", donation_quantity),
                field_row("Expiry date:", donation_expiry),
                field_row(
                    "Item image:",
                    ft.Row(
                        [
                            donation_image_path,
                            page_button("CHOOSE IMAGE", lambda e: page.run_task(choose_donation_image), bgcolor=colors["header"], width=170),
                        ],
                        spacing=12,
                        wrap=True,
                    ),
                    "Leave blank to keep the current image.",
                ),
                field_row(
                    "Current image:",
                    text_link("Open uploaded image", lambda e, url=(state["selected_donation"] or {}).get("image_url"): open_url(url))
                    if (state["selected_donation"] or {}).get("image_url")
                    else admin_text("No uploaded image", color=colors["muted"]),
                ),
                field_row(
                    "Status:",
                    ft.Container(
                        bgcolor=colors["header"],
                        padding=ft.Padding.only(left=12, right=12, top=8, bottom=8),
                        content=ft.Row([admin_text("DONATION STATUS", weight=ft.FontWeight.BOLD), ft.Container(width=12), ft.Container(width=220, content=donation_status)], spacing=8),
                    ),
                ),
            ],
            save_donation,
            delete_donation,
            clear_donation_form,
        )
        return simple_section_page(
            "Donations",
            f"{len(state['donations'])} donations",
            "ADD DONATION",
            lambda e: open_create_mode("donations"),
            donation_search,
            lambda e: page.run_task(load_donations),
            [table_cell("TITLE", 260), table_cell("DONOR", 280), table_cell("CATEGORY", 140), table_cell("STATUS", 140), table_cell("QUANTITY", 120)],
            rows,
            editor,
        )

    def select_donation(item):
        load_donation_form(item)
        render()
        page.update()

    def meetings_page():
        rows = [
            table_row(
                [
                    table_cell("", 280, control=text_link(clean_value(((item.get("claim_request") or {}).get("donation_title"))), lambda e, item=item: select_meeting(item))),
                    table_cell(format_dt(item.get("scheduled_time")), 240),
                    table_cell(clean_value(item.get("status")), 200),
                    table_cell(clean_value(item.get("meeting_link"))[:45], 320),
                ],
                active=(state["selected_meeting"] or {}).get("id") == item.get("id"),
            )
            for item in state["meetings"]
        ]
        editor = editor_panel(
            f"{'Change' if (state['selected_meeting'] or {}).get('id') else 'Add'} meeting",
            [
                field_row("Donation:", admin_text(clean_value(current_meeting_claim().get("donation_title")))),
                field_row("NGO:", admin_text(clean_value(current_meeting_claim().get("receiver_email")))),
                field_row("Scheduled time:", meeting_scheduled_time),
                field_row("Meeting link:", meeting_link),
                field_row("Meeting address:", meeting_address),
                field_row(
                    "Status:",
                    ft.Container(
                        bgcolor=colors["header"],
                        padding=ft.Padding.only(left=12, right=12, top=8, bottom=8),
                        content=ft.Row([admin_text("MEETING STATUS", weight=ft.FontWeight.BOLD), ft.Container(width=12), ft.Container(width=260, content=meeting_status)], spacing=8),
                    ),
                ),
            ],
            save_meeting,
            delete_meeting,
            clear_meeting_form,
        )
        return simple_section_page(
            "Meetings",
            f"{len(state['meetings'])} meetings",
            "ADD MEETING",
            lambda e: open_create_mode("meetings"),
            meeting_search,
            lambda e: page.run_task(load_meetings),
            [table_cell("DONATION", 280), table_cell("SCHEDULED TIME", 240), table_cell("STATUS", 200), table_cell("MEETING LINK", 320)],
            rows,
            editor,
        )

    def select_meeting(item):
        load_meeting_form(item)
        render()
        page.update()

    def section_content():
        if state["section"] == "home":
            return home_page()
        if state["section"] == "users":
            return users_page()
        if state["section"] == "claims":
            return claims_page()
        if state["section"] == "donor_profiles":
            return donor_profiles_page()
        if state["section"] == "ngo_profiles":
            return ngo_profiles_page()
        if state["section"] == "permits":
            return permits_page()
        if state["section"] == "donations":
            return donations_page()
        if state["section"] == "meetings":
            return meetings_page()
        return home_page()

    def render():
        root_host.content = build_shell(section_content())

    page.run_task(load_dashboard)
    page.run_task(load_users)
    page.run_task(load_claims)
    page.run_task(load_donor_profiles)
    page.run_task(load_ngo_profiles)
    page.run_task(load_permits)
    page.run_task(load_donations)
    page.run_task(load_meetings)
    render()

    return ft.View(
        route="/admin-panel",
        bgcolor=colors["bg"],
        controls=[root_host],
    )
