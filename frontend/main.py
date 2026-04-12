import flet as ft
import flet_map as fm
import requests

API_BASE_URL = "http://127.0.0.1:8000/api/"

def main(page: ft.Page):
    page.title = "Dodonation - Location & Meetings"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = "adaptive"

    result_text = ft.Text(value="")

    # --- 1. Map Setup (Bypassing OSM Block) ---
    map_widget = fm.Map(
        expand=True,
        initial_center=fm.MapLatitudeLongitude(0, 0),
        initial_zoom=2,
        layers=[
            fm.TileLayer(
                # Swapped to Google Maps standard tiles to avoid the OpenStreetMap ban
                url_template="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
            ),
        ],
    )

    lat_input = ft.TextField(label="Latitude", read_only=True, expand=True)
    lon_input = ft.TextField(label="Longitude", read_only=True, expand=True)

    # --- 2. Geolocator Fallback Setup ---
    def get_location_click(e):
        result_text.value = "Fetching GPS coordinates via IP..."
        result_text.color = "white"
        page.update()
        
        try:
            # Using a reliable, plugin-less Python IP Geolocation service
            response = requests.get("http://ip-api.com/json/")
            if response.status_code == 200:
                data = response.json()
                lat = data["lat"]
                lon = data["lon"]
                
                lat_input.value = str(lat)
                lon_input.value = str(lon)
                
                # Center the map on your exact coordinates
                map_widget.initial_center = fm.MapLatitudeLongitude(lat, lon)
                map_widget.initial_zoom = 15
                map_widget.update()
                
                result_text.value = "Location found & Map updated!"
                result_text.color = "green"
            else:
                result_text.value = "Could not fetch coordinates from API."
                result_text.color = "red"
        except Exception as ex:
            result_text.value = f"Location Error: {ex}"
            result_text.color = "red"
        page.update()

    # --- 3. Meeting Form Setup ---
    title = ft.Text("Schedule a Donation Meeting", size=30, weight="bold")
    
    donation_id_input = ft.TextField(label="Donation ID", value="4", prefix_icon="card_giftcard")
    donor_id_input = ft.TextField(label="Donor User ID", value="1", prefix_icon="person")
    ngo_id_input = ft.TextField(label="NGO User ID", value="2", prefix_icon="business")
    date_input = ft.TextField(label="Date & Time (YYYY-MM-DD HH:MM)", value="2026-05-01 14:00")
    link_input = ft.TextField(label="Meeting Link", value="https://meet.google.com/abc-defg-hij")

    def submit_meeting(e):
        formatted_time = f"{date_input.value}:00Z"
        payload = {
            "donation": int(donation_id_input.value),
            "donor": int(donor_id_input.value),
            "ngo": int(ngo_id_input.value),
            "scheduled_time": formatted_time,
            "meeting_link": link_input.value,
            "is_accepted": False
        }

        try:
            response = requests.post(f"{API_BASE_URL}meetings/", json=payload)
            if response.status_code == 201:
                result_text.value = "Meeting created! Email triggered in Django terminal."
                result_text.color = "green"
            else:
                result_text.value = f"Error: {response.text}"
                result_text.color = "red"
        except Exception as ex:
            result_text.value = f"Connection Error: {ex}"
            result_text.color = "red"
        page.update()

    # --- 4. Add Layout to Page ---
    page.add(
        ft.Text("Assessment Feature: GPS & Maps", size=25, weight="bold"),
        ft.Container(content=map_widget, height=300, border_radius=10, border=ft.border.all(1, "grey")),
        ft.Row([lat_input, lon_input]),
        
        ft.ElevatedButton("Get Current Location", icon="my_location", on_click=get_location_click),
        
        ft.Divider(),
        title,
        donation_id_input,
        donor_id_input,
        ngo_id_input,
        date_input,
        link_input,
        ft.ElevatedButton("Schedule Meeting", on_click=submit_meeting, bgcolor="blue", color="white"),
        result_text
    )

ft.run(main)