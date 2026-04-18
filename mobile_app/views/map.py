import requests
import flet as ft

from services.meeting_service import MeetingService
from utils.app_state import AppState
from utils.constants import PRIMARY_GREEN, SECONDARY_GREEN, BUTTON_TEXT, INPUT_TEXT
from utils.helpers import build_appbar, centered_content, page_container, section_card, show_message

try:
    import flet_map as ftm
except ImportError:
    ftm = None


def map_view(page: ft.Page):
    location_text = ft.Text("Tap a point on the map to pick the physical meeting location.", size=16, color="#4B5563")
    lat = ft.TextField(label="Latitude", width=180, color=INPUT_TEXT)
    lon = ft.TextField(label="Longitude", width=180, color=INPUT_TEXT)
    address = ft.TextField(label="Meeting Address", multiline=True, min_lines=2, color=INPUT_TEXT)

    marker_layer = None
    map_control = None
    if ftm:
        marker_layer = ftm.MarkerLayer(markers=[])

        def handle_map_tap(e):
            coordinates = e.coordinates
            lat.value = f"{coordinates.latitude:.6f}"
            lon.value = f"{coordinates.longitude:.6f}"
            marker_layer.markers = [
                ftm.Marker(
                    coordinates=coordinates,
                    content=ft.Icon(ft.Icons.LOCATION_ON, color="#B42318"),
                    width=40,
                    height=40,
                )
            ]
            location_text.value = "Location selected from the map."
            page.update()

        map_control = ftm.Map(
            expand=True,
            initial_center=ftm.MapLatitudeLongitude(-20.1609, 57.5012),
            initial_zoom=11,
            on_tap=handle_map_tap,
            layers=[
                ftm.TileLayer(url_template="https://a.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png"),
                marker_layer,
            ],
        )

    async def get_location(e):
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
                if marker_layer and map_control and lat.value and lon.value:
                    point = ftm.MapLatitudeLongitude(float(lat.value), float(lon.value))
                    marker_layer.markers = [
                        ftm.Marker(
                            coordinates=point,
                            content=ft.Icon(ft.Icons.LOCATION_ON, color="#B42318"),
                            width=40,
                            height=40,
                        )
                    ]
                    await map_control.center_on(point, zoom=14)
            else:
                location_text.value = "Could not fetch location"
        except Exception as ex:
            location_text.value = f"Error: {ex}"
        page.update()

    def save_location(e):
        if not AppState.active_meeting_id:
            show_message(page, "No active meeting selected.", "red")
            return
        if not lat.value or not lon.value:
            show_message(page, "Pick a location on the map first.", "red")
            return

        response = MeetingService.set_meeting_location(
            AppState.active_meeting_id,
            latitude=lat.value,
            longitude=lon.value,
            address=address.value,
        )

        if response.status_code == 200:
            show_message(page, "Meeting point pinned for the NGO.", "green")
            location_text.value = "Meeting location pinned."
            page.update()
        else:
            show_message(page, f"Could not save meeting location: {response.text}", "red")

    async def go_back(e):
        await page.push_route("/meetings")

    map_section_controls = []
    if map_control:
        map_section_controls.append(
            ft.Container(
                content=map_control,
                height=360,
                border_radius=18,
                clip_behavior=ft.ClipBehavior.HARD_EDGE,
            )
        )
    else:
        map_section_controls.append(
            ft.Container(
                padding=16,
                bgcolor="#FFF4E5",
                border_radius=16,
                content=ft.Text(
                    "Interactive map requires the optional 'flet-map' package. "
                    "Install it in your virtualenv to enable tap-to-pick mapping.",
                    color="#7A4F01",
                ),
            )
        )

    return ft.View(
        route="/map",
        appbar=build_appbar("Meeting Map", go_back),
        controls=[
            page_container(
                centered_content(
                    section_card(
                        "Pick Meeting Point",
                        [location_text] + map_section_controls,
                        subtitle="Choose the physical handoff point after the online meeting is complete.",
                    ),
                    section_card(
                        "Location Details",
                        [
                            address,
                            ft.Row([lat, lon], wrap=True, spacing=12),
                            ft.Row(
                                [
                                    ft.Button("Use My Current Area", on_click=get_location, bgcolor=SECONDARY_GREEN, color=BUTTON_TEXT),
                                    ft.Button("Save Meeting Location", on_click=save_location, bgcolor=PRIMARY_GREEN, color=BUTTON_TEXT),
                                ],
                                wrap=True,
                                spacing=12,
                            ),
                        ],
                    ),
                    ft.Row(
                        [ft.Button("Back", on_click=go_back, bgcolor="#666666", color=BUTTON_TEXT, width=140)],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                ),
            )
        ],
    )
