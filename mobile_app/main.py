import flet as ft
from views.login import login_view
from views.role_selection import role_selection_view
from views.register import register_donor_view, register_ngo_view
from views.otp import otp_view
from views.dashboard import dashboard_view
from views.chatbot import chatbot_view
from views.map import map_view
from views.donations import donations_view
from views.claims import claims_view
from views.profile import profile_view
from views.permits import permits_view
from views.meetings import meetings_view

def main(page: ft.Page):
    page.title = "Donation App"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 400
    page.window_height = 700

    def build_views():
        page.views.clear()

        # Always add a root view
        if page.route == "/":
            page.views.append(login_view(page))
        elif page.route == "/role-selection":
            page.views.append(role_selection_view(page))
        elif page.route == "/register/donor":
            page.views.append(register_donor_view(page))
        elif page.route == "/register/ngo":
            page.views.append(register_ngo_view(page))
        elif page.route == "/otp":
            page.views.append(otp_view(page))
        elif page.route == "/dashboard":
            page.views.append(dashboard_view(page))
        elif page.route == "/donations":
            page.views.append(donations_view(page))
        elif page.route == "/claims":
            page.views.append(claims_view(page))
        elif page.route == "/profile":
            page.views.append(profile_view(page))
        elif page.route == "/permits":
            page.views.append(permits_view(page))
        elif page.route == "/meetings":
            page.views.append(meetings_view(page))
        elif page.route == "/chatbot":
            page.views.append(chatbot_view(page))
        elif page.route == "/map":
            page.views.append(map_view(page))
        else:
            page.views.append(
                ft.View(
                    route="/",
                    controls=[ft.Text("Route not found")],
                )
            )

        page.update()

    def route_change(e: ft.RouteChangeEvent):
        build_views()

    async def view_pop(e: ft.ViewPopEvent):
        page.views.pop()
        top_view = page.views[-1]
        await page.push_route(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    # Initial render
    build_views()

if __name__ == "__main__":
    ft.run(main)
