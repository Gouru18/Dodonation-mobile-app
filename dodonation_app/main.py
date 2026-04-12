import flet as ft

def main(page: ft.Page):
    page.title = "Dodonation App"
    page.theme_mode = ft.ThemeMode.LIGHT

    def route_change(e: ft.RouteChangeEvent):
        page.views.clear()

        if page.route == "/":
            page.views.append(
                ft.View(
                    route="/",
                    appbar=ft.AppBar(title=ft.Text("Welcome to Dodonation")),
                    controls=[
                        ft.Container(
                            expand=True,
                            padding=20,
                            content=ft.Column(
                                controls=[
                                    ft.Text(
                                        "Select Your Role",
                                        size=24,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.FilledButton(
                                        "Donor",
                                        width=300,
                                        on_click=lambda e: page.go("/login"),
                                    ),
                                    ft.FilledButton(
                                        "NGO",
                                        width=300,
                                        on_click=lambda e: page.go("/ngo_permit"),
                                    ),
                                    ft.FilledButton(
                                        "Chatbot",
                                        width=300,
                                        on_click=lambda e: page.go("/chatbot"),
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=20,
                            ),
                        )
                    ],
                )
            )

        elif page.route == "/login":
            page.views.append(
                ft.View(
                    route="/login",
                    appbar=ft.AppBar(title=ft.Text("Login")),
                    controls=[
                        ft.Container(
                            expand=True,
                            padding=20,
                            content=ft.Column(
                                controls=[
                                    ft.TextField(label="Email", width=300),
                                    ft.TextField(label="Password", password=True, width=300),
                                    ft.FilledButton(
                                        "Login",
                                        width=300,
                                        on_click=lambda e: page.go("/"),
                                    ),
                                    ft.TextButton(
                                        "Register",
                                        on_click=lambda e: page.go("/register"),
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=20,
                            ),
                        )
                    ],
                )
            )

        elif page.route == "/register":
            page.views.append(
                ft.View(
                    route="/register",
                    appbar=ft.AppBar(title=ft.Text("Register")),
                    controls=[
                        ft.Container(
                            expand=True,
                            padding=20,
                            content=ft.Column(
                                controls=[
                                    ft.TextField(label="Name", width=300),
                                    ft.TextField(label="Email", width=300),
                                    ft.TextField(label="Password", password=True, width=300),
                                    ft.FilledButton(
                                        "Register",
                                        width=300,
                                        on_click=lambda e: page.go("/"),
                                    ),
                                    ft.TextButton(
                                        "Login",
                                        on_click=lambda e: page.go("/login"),
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=20,
                            ),
                        )
                    ],
                )
            )

        elif page.route == "/ngo_permit":
            page.views.append(
                ft.View(
                    route="/ngo_permit",
                    appbar=ft.AppBar(title=ft.Text("NGO Permit")),
                    controls=[
                        ft.Container(
                            expand=True,
                            padding=20,
                            content=ft.Column(
                                controls=[
                                    ft.Text("NGO Permit Application", size=20),
                                    ft.TextField(label="NGO Name", width=300),
                                    ft.TextField(label="Registration Number", width=300),
                                    ft.FilledButton(
                                        "Submit",
                                        width=300,
                                        on_click=lambda e: page.go("/"),
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=20,
                            ),
                        )
                    ],
                )
            )

        elif page.route == "/chatbot":
            page.views.append(
                ft.View(
                    route="/chatbot",
                    appbar=ft.AppBar(title=ft.Text("Chatbot")),
                    controls=[
                        ft.Container(
                            expand=True,
                            padding=20,
                            content=ft.Column(
                                controls=[
                                    ft.Text("Chatbot Interface", size=20),
                                    ft.TextField(label="Ask something", width=300),
                                    ft.FilledButton(
                                        "Send",
                                        width=300,
                                        on_click=lambda e: None,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=20,
                            ),
                        )
                    ],
                )
            )

        else:
            page.views.append(
                ft.View(
                    route=page.route,
                    appbar=ft.AppBar(title=ft.Text("Page not found")),
                    controls=[ft.Text(f"No view for route: {page.route}")],
                )
            )

        page.update()

    def view_pop(e: ft.ViewPopEvent):
        page.views.pop()
        if page.views:
            top_view = page.views[-1]
            page.go(top_view.route)

    def on_error(e):
        print("FLET ERROR:", e)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.on_error = on_error

    page.go("/")

if __name__ == "__main__":
    ft.run(main)