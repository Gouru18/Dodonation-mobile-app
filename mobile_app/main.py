import flet as ft

from services.auth_service import AuthService
from views.login import login_view
from views.role_selection import role_selection_view
from views.register import register_donor_view, register_ngo_view
from views.otp import otp_view
from views.dashboard import dashboard_view
from views.map import map_view
from views.donations import donations_view
from views.claims import claims_view
from views.profile import profile_view
from views.permits import permits_view
from views.meetings import meetings_view
from views.admin_panel import admin_panel_view


PUBLIC_ROUTES = {
    "/",
    "/role-selection",
    "/register/donor",
    "/register/ngo",
    "/otp",
}


def main(page: ft.Page):
    page.title = "Dodonation"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 430
    page.window_height = 760
    page.window_min_width = 380
    page.window_min_height = 680
    page.bgcolor = "#F4F7F1"
    page.padding = 0
    page.scroll = ft.ScrollMode.AUTO

    def not_found_view():
        return ft.View(
            route="/404",
            controls=[
                ft.Container(
                    expand=True,
                    alignment=ft.alignment.center,
                    padding=24,
                    content=ft.Column(
                        [
                            ft.Icon(ft.Icons.ERROR_OUTLINE, size=56, color="#B42318"),
                            ft.Text(
                                "Page not found",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color="#1F2937",
                            ),
                            ft.Text(
                                "The route you tried to open does not exist.",
                                color="#4B5563",
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.ElevatedButton(
                                "Go to Login",
                                on_click=lambda e: page.go("/"),
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=14,
                    ),
                )
            ],
        )

    def build_view_for_route(route: str):
        if route == "/":
            return login_view(page)
        if route == "/role-selection":
            return role_selection_view(page)
        if route == "/register/donor":
            return register_donor_view(page)
        if route == "/register/ngo":
            return register_ngo_view(page)
        if route == "/otp":
            return otp_view(page)
        if route == "/dashboard":
            return dashboard_view(page)
        if route == "/donations":
            return donations_view(page)
        if route == "/claims":
            return claims_view(page)
        if route == "/profile":
            return profile_view(page)
        if route == "/permits":
            return permits_view(page)
        if route == "/meetings":
            return meetings_view(page)
        if route == "/map":
            return map_view(page)
        if route == "/admin-panel":
            return admin_panel_view(page)
        return not_found_view()

    async def build_views():
        await AuthService.restore_session(page)

        target_route = page.route or "/"

        if target_route not in PUBLIC_ROUTES and not AuthService.is_authenticated():
            target_route = "/"

        page.views.clear()
        page.views.append(build_view_for_route(target_route))
        page.update()

    def route_change(e: ft.RouteChangeEvent):
        page.run_task(build_views)

    async def view_pop(e: ft.ViewPopEvent):
        if len(page.views) > 1:
            page.views.pop()
            await page.push_route(page.views[-1].route)
        else:
            await page.push_route("/")

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    page.run_task(build_views)


if __name__ == "__main__":
    ft.run(main)
    