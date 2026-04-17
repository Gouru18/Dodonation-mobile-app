import flet as ft
from utils.constants import PRIMARY_GREEN, BUTTON_TEXT, INPUT_TEXT
from utils.helpers import show_message
import requests

def map_view(page: ft.Page):
    location_text = ft.Text("Location unknown", size=16)
    lat = ft.TextField(label="Latitude", width=180, read_only=True, color=INPUT_TEXT)
    lon = ft.TextField(label="Longitude", width=180, read_only=True, color=INPUT_TEXT)

    def get_location(e):
        try:
            response = requests.get("http://ip-api.com/json/", timeout=5)
            if response.status_code == 200:
                data = response.json()
                lat.value = str(data.get("lat", ""))
                lon.value = str(data.get("lon", ""))
                location_text.value = f"Location: {data.get('city', 'Unknown')}, {data.get('country', '')}"
            else:
                location_text.value = "Could not fetch location"
        except Exception as ex:
            location_text.value = f"Error: {ex}"
        page.update()

    async def go_back(e):
        await page.push_route("/dashboard")

    return ft.View(
        route="/map",
        appbar=ft.AppBar(title=ft.Text("Donation App - Map")),
        controls=[
            ft.Container(
                expand=True,
                padding=20,
                content=ft.Column(
                    [
                        location_text,
                        ft.Row([lat, lon], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Button("Get Location", on_click=get_location, bgcolor=PRIMARY_GREEN, color=BUTTON_TEXT),
                        ft.Button("Back", on_click=go_back, bgcolor="#444", color=BUTTON_TEXT),
                    ],
                    spacing=15,
                ),
            )
        ],
    )
