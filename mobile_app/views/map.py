import requests
import flet as ft

from services.meeting_service import MeetingService
from utils.app_state import AppState
from utils.helpers import (
    build_appbar,
    centered_content,
    page_container,
    section_card,
    auth_input,
    primary_button,
    secondary_button,
    muted_text,
    show_error,
    show_success,
)

try:
    import flet_map as ftm
except ImportError:
    ftm = None


def map_view(page: ft.Page):
    state = {
        "meeting_loaded": False,
        "can_pin_location": False,
        "location_saved": False,
    }

    location_text = ft.Text(
        "Tap a point on the map to pick the physical meeting location.",
        size=16,
        color="#4B5563",
    )
    save_notice = ft.Container(
        visible=False,
        padding=16,
        border_radius=16,
        bgcolor="#ECFDF3",
        border=ft.Border.all(1, "#ABEFC6"),
    )

    lat = auth_input("Latitude", ft.Icons.MY_LOCATION)
    lon = auth_input("Longitude", ft.Icons.PLACE)
    address = auth_input("Meeting Address", ft.Icons.HOME, multiline=True)
    address.min_lines = 2

    lat.read_only = True
    lon.read_only = True

    marker_layer = None
    map_control = None

    if ftm:
        marker_layer = ftm.MarkerLayer(markers=[])

        def handle_map_tap(e):
            if not state["can_pin_location"]:
                show_error(page, "This meeting is not ready for location pinning yet.")
                return

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

    async def load_meeting_context():
        if not AppState.active_meeting_id:
            location_text.value = "No active meeting selected."
            page.update()
            return

        response = MeetingService.get_meeting_detail(AppState.active_meeting_id)
        if response.status_code != 200:
            location_text.value = "Could not load meeting details."
            show_error(page, f"Could not load meeting details: {response.text}")
            page.update()
            return

        meeting = response.json()
        state["meeting_loaded"] = True
        state["can_pin_location"] = bool(meeting.get("can_pin_location"))

        if meeting.get("meeting_latitude") is not None:
            lat.value = str(meeting.get("meeting_latitude"))
        if meeting.get("meeting_longitude") is not None:
            lon.value = str(meeting.get("meeting_longitude"))
        address.value = meeting.get("meeting_address") or ""

        if state["can_pin_location"]:
            location_text.value = "Tap a point on the map to pick the physical meeting location."
        elif lat.value and lon.value:
            location_text.value = "A physical meeting point has already been pinned."
        else:
            location_text.value = "You can pin the location only after the online meeting is completed."
            state["location_saved"] = False
            save_notice.visible = False
            save_notice.content = None

        if lat.value and lon.value:
            state["location_saved"] = True
            save_notice.visible = True
            save_notice.content = ft.Column(
                [
                    ft.Text(
                        "Meeting Location Saved",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color="#166534",
                    ),
                    muted_text("A physical handoff point has already been saved for this meeting."),
                ],
                spacing=8,
            )

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

        page.update()

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
                show_error(page, "Could not fetch current area.")
        except Exception as ex:
            show_error(page, f"Error: {ex}")

        page.update()

    def save_location(e):
        if not AppState.active_meeting_id:
            show_error(page, "No active meeting selected.")
            return

        if not state["can_pin_location"]:
            show_error(page, "This meeting is not ready for location pinning.")
            return

        if not lat.value or not lon.value:
            show_error(page, "Pick a location on the map first.")
            return

        response = MeetingService.set_meeting_location(
            AppState.active_meeting_id,
            latitude=lat.value,
            longitude=lon.value,
            address=address.value,
        )

        if response.status_code == 200:
            state["can_pin_location"] = False
            state["location_saved"] = True
            show_success(page, "Meeting point pinned successfully.")
            location_text.value = "Meeting location pinned successfully."
            save_notice.visible = True
            save_notice.content = ft.Column(
                [
                    ft.Text(
                        "Meeting Location Saved",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color="#166534",
                    ),
                    muted_text("The meeting point is saved. Return to Meetings to continue the handoff workflow."),
                ],
                spacing=8,
            )
            page.update()
        else:
            show_error(page, f"Could not save meeting location: {response.text}")

    async def go_back(e):
        await page.push_route("/meetings")

    page.run_task(load_meeting_context)

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
                                    secondary_button(
                                        "Use My Current Area",
                                        get_location,
                                        width=190,
                                        icon=ft.Icons.MY_LOCATION,
                                    ),
                                    primary_button(
                                        "Save Meeting Location",
                                        save_location,
                                        width=220,
                                        icon=ft.Icons.SAVE,
                                    ),
                                ],
                                wrap=True,
                                spacing=12,
                            ),
                            save_notice,
                            muted_text(
                                "Either the donor or NGO can pin the physical handoff point after the online meeting is completed."
                            ),
                        ],
                    ),
                    ft.Row(
                        [
                            secondary_button(
                                "Back",
                                go_back,
                                width=140,
                                icon=ft.Icons.ARROW_BACK,
                            )
                        ],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                ),
            )
        ],
    )
