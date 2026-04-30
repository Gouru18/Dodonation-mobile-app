import platform
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

try:
    import flet_geolocator as ftg
except ImportError:
    ftg = None


def map_view(page: ft.Page):
    def route_meeting_id():
        parts = (page.route or "").strip("/").split("/")
        if len(parts) == 2 and parts[0] == "map" and parts[1]:
            return parts[1]
        return None

    active_meeting_id = route_meeting_id() or AppState.active_meeting_id
    if active_meeting_id:
        AppState.active_meeting_id = active_meeting_id

    is_windows = platform.system().lower().startswith("win")

    state = {
        "meeting_loaded": False,
        "can_pin_location": False,
        "location_saved": False,
        "location_permission_granted": ftg is None and not is_windows,
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
        content=ft.Column(
            [
                ft.Text(
                    "No meeting location has been pinned yet.",
                    size=14,
                    color="#166534",
                ),
                muted_text("The donor or NGO can pin the location after the online meeting is completed."),
            ],
            spacing=6,
        ),
    )
    lat = auth_input("Latitude", ft.Icons.MY_LOCATION)
    lon = auth_input("Longitude", ft.Icons.PLACE)
    address = auth_input("Meeting Address", ft.Icons.HOME, multiline=True)
    address.min_lines = 2

    lat.hint_text = "Tap map, search address, or type latitude"
    lon.hint_text = "Tap map, search address, or type longitude"

    marker_layer = None
    map_control = None
    map_permission_gate = None
    current_dialog = None
    url_launcher = ft.UrlLauncher()
    geolocator = None

    map_error_notice = ft.Container(
        visible=False,
        padding=12,
        border_radius=12,
        bgcolor="#FFF4E5",
        border=ft.Border.all(1, "#FEDF89"),
        content=muted_text(
            "Map tiles could not load. Check the phone's internet connection, then use the coordinate fields or try again.",
        ),
    )
    location_permission_notice = ft.Container(
        visible=bool((geolocator or is_windows) and not state["location_permission_granted"]),
        padding=12,
        border_radius=12,
        bgcolor="#EFF6FF",
        border=ft.Border.all(1, "#BFDBFE"),
        content=muted_text(
            "Please allow location access so the app can use your device location for the meeting map. "
            "Click Allow when prompted.",
        ),
    )

    if ftg:
        geolocator = ftg.Geolocator(
            configuration=ftg.GeolocatorConfiguration(
                accuracy=ftg.GeolocatorPositionAccuracy.LOW,
            ),
        )

    def has_coordinates():
        return bool(normalize_coordinate(lat.value) and normalize_coordinate(lon.value))

    def normalize_coordinate(value):
        raw = str(value or "").strip()
        if not raw:
            return ""
        try:
            return f"{float(raw):.6f}"
        except (TypeError, ValueError):
            return raw

    def validate_coordinates():
        try:
            latitude = float(str(lat.value or "").strip())
            longitude = float(str(lon.value or "").strip())
        except (TypeError, ValueError):
            return None, None, "Latitude and longitude must be valid numbers."

        if latitude < -90 or latitude > 90:
            return None, None, "Latitude must be between -90 and 90."
        if longitude < -180 or longitude > 180:
            return None, None, "Longitude must be between -180 and 180."

        return latitude, longitude, None

    async def update_marker(latitude, longitude, zoom=14):
        if not marker_layer or not map_control:
            return

        point = ftm.MapLatitudeLongitude(latitude, longitude)
        marker_layer.markers = [
            ftm.Marker(
                coordinates=point,
                content=ft.Icon(ft.Icons.LOCATION_ON, color="#B42318"),
                width=40,
                height=40,
            )
        ]
        await map_control.center_on(point, zoom=zoom)

    def close_dialog():
        nonlocal current_dialog
        if current_dialog:
            current_dialog.open = False
            current_dialog = None
            page.update()

    def open_dialog(title, content_controls, actions, modal=True):
        nonlocal current_dialog
        dialog = ft.AlertDialog(
            modal=modal,
            title=ft.Text(title, weight=ft.FontWeight.BOLD),
            content=ft.Column(content_controls, tight=True, spacing=10),
            actions=actions,
            actions_alignment=ft.MainAxisAlignment.END,
        )
        current_dialog = dialog
        page.show_dialog(dialog)

    def permission_is_granted(status):
        if not ftg or status is None:
            return False
        return status in (
            ftg.GeolocatorPermissionStatus.ALWAYS,
            ftg.GeolocatorPermissionStatus.WHILE_IN_USE,
        )

    def update_location_permission_ui():
        if map_permission_gate:
            map_permission_gate.visible = bool(geolocator and not state["location_permission_granted"])
        location_permission_notice.visible = bool((geolocator or is_windows) and not state["location_permission_granted"])

    async def open_app_settings(e):
        if geolocator:
            close_dialog()
            try:
                await geolocator.open_app_settings()
            except Exception as ex:
                show_error(page, f"Could not open app settings: {ex}")

    async def ensure_location_permission(action_label="use location features"):
        if not geolocator:
            return True

        try:
            status = await geolocator.get_permission_status()
            if permission_is_granted(status):
                state["location_permission_granted"] = True
                update_location_permission_ui()
                page.update()
                return True

            status = await geolocator.request_permission()
            if permission_is_granted(status):
                state["location_permission_granted"] = True
                update_location_permission_ui()
                page.update()
                return True

            state["location_permission_granted"] = False
            update_location_permission_ui()
            if status == ftg.GeolocatorPermissionStatus.DENIED_FOREVER:
                open_dialog(
                    "Location Permission Needed",
                    [
                        muted_text(
                            "Location access is blocked for this app. Enable it in app settings to use map location features."
                        ),
                    ],
                    [
                        ft.TextButton("Cancel", on_click=lambda e: close_dialog()),
                        ft.TextButton("Open Settings", on_click=open_app_settings),
                    ],
                )
            else:
                show_error(page, f"Location permission is required to {action_label}.")
            page.update()
            return False
        except Exception as ex:
            show_error(page, f"Could not request location permission: {ex}")
            return False

    async def refresh_location_permission_status():
        if not geolocator:
            state["location_permission_granted"] = not is_windows
            update_location_permission_ui()
            page.update()
            return

        try:
            status = await geolocator.get_permission_status()
            state["location_permission_granted"] = permission_is_granted(status)
            update_location_permission_ui()
            page.update()
        except Exception:
            state["location_permission_granted"] = False
            update_location_permission_ui()
            page.update()

    async def allow_windows_location(e):
        close_dialog()
        state["location_permission_granted"] = True
        update_location_permission_ui()
        location_text.value = "Location access allowed. Fetching your current location..."
        page.update()
        await perform_get_location()

    async def prompt_windows_location_permission(e=None):
        open_dialog(
            "Allow Location Access",
            [
                muted_text(
                    "To use current location on Windows, please allow the app to access your location. "
                    "Click Allow to continue."
                )
            ],
            [
                ft.TextButton("Cancel", on_click=lambda e: close_dialog()),
                ft.TextButton("Allow", on_click=allow_windows_location),
            ],
        )

    async def request_map_permission(e):
        if await ensure_location_permission("open the map"):
            location_text.value = "Location permission granted. You can now use the map."
            page.update()

    def show_confirm_notice():
        open_dialog(
            "Save Meeting Location",
            [
                muted_text("Save this meeting location for the physical handoff?"),
                muted_text(f"Latitude: {lat.value or 'Not selected'}"),
                muted_text(f"Longitude: {lon.value or 'Not selected'}"),
                muted_text(f"Address: {address.value or 'Not provided'}"),
            ],
            [
                ft.TextButton("Cancel", on_click=lambda e: close_dialog()),
                ft.TextButton("Confirm Save", on_click=lambda e: persist_location()),
            ],
        )

    async def reverse_geocode(latitude, longitude):
        try:
            response = requests.get(
                "https://nominatim.openstreetmap.org/reverse",
                params={
                    "lat": latitude,
                    "lon": longitude,
                    "format": "jsonv2",
                },
                headers={"User-Agent": "DodonationApp/1.0"},
                timeout=8,
            )
            if response.status_code == 200:
                data = response.json()
                display_name = data.get("display_name")
                if display_name:
                    address.value = display_name
                    location_text.value = "Location selected and address resolved."
                    page.update()
                    return
        except Exception:
            pass

        location_text.value = "Location selected from the map. Address could not be resolved."
        page.update()

    if ftm:
        marker_layer = ftm.MarkerLayer(markers=[])

        def handle_tile_error(e):
            map_error_notice.visible = True
            page.update()

        async def handle_map_tap(e):
            if not state["can_pin_location"]:
                show_error(page, "This meeting is not ready for location pinning yet.")
                return
            if not state["location_permission_granted"]:
                show_error(page, "Allow location permission before using the map.")
                return
            if not await ensure_location_permission("pin a meeting point on the map"):
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
            page.run_task(reverse_geocode, coordinates.latitude, coordinates.longitude)
            page.update()

        map_control = ftm.Map(
            bgcolor="#E5E7EB",
            keep_alive=True,
            initial_center=ftm.MapLatitudeLongitude(-20.1609, 57.5012),
            initial_zoom=11,
            on_tap=handle_map_tap,
            layers=[
                ftm.TileLayer(
                    url_template="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
                    subdomains=["a", "b", "c"],
                    user_agent_package_name="com.dodonation.mobile",
                    fallback_url="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                    max_native_zoom=19,
                    on_image_error=handle_tile_error,
                ),
                marker_layer,
            ],
        )

    async def load_meeting_context():
        meeting_id = route_meeting_id() or AppState.active_meeting_id
        if not meeting_id:
            location_text.value = "No active meeting selected."
            page.update()
            return

        AppState.active_meeting_id = meeting_id
        response = MeetingService.get_meeting_detail(meeting_id)
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
            location_text.value = "A physical handoff point has already been saved for this meeting."
        else:
            save_notice.visible = False
            save_notice.content = None

        save_button.disabled = not state["can_pin_location"] or state["location_saved"]

        if marker_layer and map_control and lat.value and lon.value:
            latitude, longitude, coordinate_error = validate_coordinates()
            if not coordinate_error:
                await update_marker(latitude, longitude)

        page.update()

    async def search_address(e):
        if not await ensure_location_permission("search and preview locations on the map"):
            return

        query = (address.value or "").strip()
        if not query:
            show_error(page, "Enter a meeting address to search.")
            return

        try:
            response = requests.get(
                "https://nominatim.openstreetmap.org/search",
                params={
                    "q": query,
                    "format": "jsonv2",
                    "limit": 1,
                },
                headers={"User-Agent": "DodonationApp/1.0"},
                timeout=8,
            )
            if response.status_code != 200:
                show_error(page, "Could not search this address.")
                return

            results = response.json()
            if not results:
                show_error(page, "No location found for that address.")
                return

            result = results[0]
            latitude = float(result["lat"])
            longitude = float(result["lon"])
            lat.value = f"{latitude:.6f}"
            lon.value = f"{longitude:.6f}"
            address.value = result.get("display_name") or query
            location_text.value = "Location found from the address."
            await update_marker(latitude, longitude)
            page.update()
        except Exception as ex:
            show_error(page, f"Could not search address: {ex}")

    async def perform_get_location():
        try:
            if geolocator:
                service_enabled = await geolocator.is_location_service_enabled()
                if not service_enabled:
                    show_error(page, "Turn on location services to use your current location.")
                    return

                position = await geolocator.get_current_position()
                lat.value = f"{position.latitude:.6f}"
                lon.value = f"{position.longitude:.6f}"
                location_text.value = "Current location selected."

                if marker_layer and map_control:
                    await update_marker(position.latitude, position.longitude)
                await reverse_geocode(position.latitude, position.longitude)
                page.update()
                return

            response = requests.get("http://ip-api.com/json/", timeout=5)
            if response.status_code != 200:
                show_error(page, "Could not fetch current area.")
                return

            data = response.json()
            lat.value = str(data.get("lat", ""))
            lon.value = str(data.get("lon", ""))
            address.value = ", ".join(
                [part for part in [data.get("city"), data.get("regionName"), data.get("country")] if part]
            )
            location_text.value = f"Suggested location: {address.value}"

            if marker_layer and map_control and lat.value and lon.value:
                await update_marker(float(lat.value), float(lon.value))
        except Exception as ex:
            show_error(page, f"Error: {ex}")

        page.update()

    async def get_location(e):
        if geolocator:
            if not await ensure_location_permission("use your current location"):
                return
            await perform_get_location()
            return

        if is_windows and not state["location_permission_granted"]:
            await prompt_windows_location_permission()
            return

        await perform_get_location()

    def save_location(e):
        meeting_id = route_meeting_id() or AppState.active_meeting_id
        if not meeting_id:
            show_error(page, "No active meeting selected.")
            return

        if not state["can_pin_location"]:
            show_error(page, "This meeting is not ready for location pinning.")
            return

        latitude, longitude, coordinate_error = validate_coordinates()
        if coordinate_error:
            show_error(page, coordinate_error)
            return

        lat.value = f"{latitude:.6f}"
        lon.value = f"{longitude:.6f}"

        show_confirm_notice()

    def persist_location():
        meeting_id = route_meeting_id() or AppState.active_meeting_id
        if not meeting_id:
            show_error(page, "No active meeting selected.")
            return

        close_dialog()
        response = MeetingService.set_meeting_location(
            meeting_id,
            latitude=lat.value,
            longitude=lon.value,
            address=address.value,
        )

        if response.status_code == 200:
            verify_response = MeetingService.get_meeting_detail(meeting_id)
            if verify_response.status_code != 200:
                show_error(page, "Location was submitted, but verification failed when reloading the meeting.")
                return

            saved_meeting = verify_response.json()
            saved_lat = normalize_coordinate(saved_meeting.get("meeting_latitude"))
            saved_lon = normalize_coordinate(saved_meeting.get("meeting_longitude"))
            saved_address = saved_meeting.get("meeting_address") or ""
            if (
                saved_lat != normalize_coordinate(lat.value)
                or saved_lon != normalize_coordinate(lon.value)
                or saved_address != (address.value or "")
                or saved_meeting.get("status") != "location_pinned"
            ):
                show_error(page, "Meeting location save could not be confirmed from the backend.")
                return

            state["can_pin_location"] = False
            state["location_saved"] = True
            save_button.disabled = True
            show_success(page, "Meeting point pinned successfully.")
            location_text.value = "Meeting location pinned successfully."
            open_dialog(
                "Location Saved",
                [
                    muted_text("The meeting point is saved. Return to Meetings to continue the handoff workflow."),
                    muted_text(f"Latitude: {saved_lat}"),
                    muted_text(f"Longitude: {saved_lon}"),
                    muted_text(f"Address: {saved_address or 'Not provided'}"),
                ],
                [ft.TextButton("OK", on_click=lambda e: close_dialog())],
            )
            page.update()
        else:
            show_error(page, f"Could not save meeting location: {response.status_code} - {response.text}")
            page.update()

    async def go_back(e):
        await page.push_route("/meetings")

    save_button = primary_button(
        "Save Meeting Location",
        save_location,
        width=220,
        icon=ft.Icons.SAVE,
    )
    save_button.disabled = True

    page.run_task(load_meeting_context)
    page.run_task(refresh_location_permission_status)
    view_services = [url_launcher]
    if geolocator:
        view_services.append(geolocator)

    map_section_controls = []
    if map_control:
        map_permission_gate = ft.Container(
            visible=bool(geolocator and not state["location_permission_granted"]),
            expand=True,
            alignment=ft.Alignment.CENTER,
            bgcolor="#F8FAFCCC",
            padding=24,
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.LOCATION_ON, size=42, color="#166534"),
                    ft.Text(
                        "Location Permission Required",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color="#1F2937",
                    ),
                    muted_text(
                        "Please allow location access so the app can use your device location for the meeting map.",
                        text_align=ft.TextAlign.CENTER,
                    ),
                    primary_button(
                        "Allow Location Access",
                        request_map_permission,
                        width=220,
                        icon=ft.Icons.MY_LOCATION,
                    ),
                ],
                spacing=12,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        )
        map_section_controls.append(
            ft.Container(
                content=ft.Stack(
                    [
                        map_control,
                        map_permission_gate,
                    ],
                    expand=True,
                ),
                height=320 if (page.width or 430) < 700 else 420,
                border_radius=18,
                clip_behavior=ft.ClipBehavior.HARD_EDGE,
            )
        )
        map_section_controls.append(location_permission_notice)
        map_section_controls.append(map_error_notice)
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
        services=view_services,
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
                                    secondary_button(
                                        "Find Address",
                                        search_address,
                                        width=160,
                                        icon=ft.Icons.SEARCH,
                                    ),
                                    save_button,
                                ],
                                wrap=True,
                                spacing=12,
                            ),
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
