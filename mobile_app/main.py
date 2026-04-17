import flet as ft
from views.login import login_view
from views.register import register_view
from views.dashboard import dashboard_view
from views.chatbot import chatbot_view
from views.map import map_view


def main(page: ft.Page):
    page.title = "Donation App"
    page.views.clear()

    def route_change(e: ft.RouteChangeEvent):
        page.views.clear()

        if page.route == "/":
            page.views.append(login_view(page))
        elif page.route == "/register":
            page.views.append(register_view(page))
        elif page.route == "/dashboard":
            page.views.append(dashboard_view(page))
        elif page.route == "/chatbot":
            page.views.append(chatbot_view(page))
        elif page.route == "/map":
            page.views.append(map_view(page))

        page.update()

    page.on_route_change = route_change
    page.go("/")


if __name__ == "__main__":
    ft.run(main)
