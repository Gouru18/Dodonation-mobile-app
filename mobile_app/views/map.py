import flet as ft
from services.meeting_service import MeetingService
from utils.app_state import AppState
from utils.constants import PRIMARY_GREEN, BUTTON_TEXT, INPUT_TEXT
from utils.helpers import show_message
import requests

def map_view(page: ft.Page):
    location_text = ft.Text("Meeting location not set yet", size=16)
    lat = ft.TextField(label="Latitude", width=180, color=INPUT_TEXT)
    lon = ft.TextField(label="Longitude", width=180, color=INPUT_TEXT)
    address = ft.TextField(label="Meeting Address", multiline=True, min_lines=2, color=INPUT_TEXT)

    def get_location(e):
        try:
            response = requests.get("http://ip-api.com/json/", timeout=5)
            if response.status_code == 200:
                data = response.json()
                lat.value = str(data.get("lat", ""))
                lon.value = str(data.get("lon", ""))
                address.value = ", ".join(
                    [part for part in [data.get("city"), data.get("regionName"), data.get("country")] if part]
                )
                location_text.value = f"Suggested location: {address.value}"
            else:
                location_text.value = "Could not fetch location"
        except Exception as ex:
            location_text.value = f"Error: {ex}"
        page.update()

    def save_location(e):
        if not AppState.active_meeting_id:
            show_message(page, "No active meeting selected.", "red")
            return

        response = MeetingService.set_meeting_location(
            AppState.active_meeting_id,
            latitude=lat.value,
            longitude=lon.value,
            address=address.value,
        )

        if response.status_code == 200:
            show_message(page, "Meeting location saved.", "green")
            location_text.value = "Meeting location updated."
            page.update()
        else:
            show_message(page, f"Could not save meeting location: {response.text}", "red")

    async def go_back(e):
        await page.push_route("/meetings")

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
                        address,
                        ft.Row([lat, lon], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Button("Get Location", on_click=get_location, bgcolor=PRIMARY_GREEN, color=BUTTON_TEXT),
                        ft.Button("Save Meeting Location", on_click=save_location, bgcolor=PRIMARY_GREEN, color=BUTTON_TEXT),
                        ft.Button("Back", on_click=go_back, bgcolor="#444", color=BUTTON_TEXT),
                    ],
                    spacing=15,
                ),
            )
        ],
    )
