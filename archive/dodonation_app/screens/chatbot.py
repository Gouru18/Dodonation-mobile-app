# pylint: disable=E1121, E1123
import flet as ft
from mobile_app.utils.helpers import form_container, show_message, clear_page
from mobile_app.utils.config import PRIMARY_GREEN, SECONDARY_GREEN, BUTTON_TEXT, INPUT_TEXT
import requests

def chatbot_screen(page, go_back):
    clear_page(page)

    chat_history = ft.Column(scroll=ft.ScrollMode.AUTO, height=400)
    message_input = ft.TextField(
        label="Type your message",
        bgcolor=INPUT_TEXT,
        color="#000000",
        border_color=PRIMARY_GREEN,
        width=300
    )

    def send_message(e):
        user_message = message_input.value.strip()
        if not user_message:
            show_message(page, "Please enter a message.", "error")
            return

        # Add user message to chat
        chat_history.controls.append(
            ft.Container(
                content=ft.Text(f"You: {user_message}", color="#000000"),
                bgcolor=SECONDARY_GREEN,
                padding=10,
                border_radius=10,
                margin=ft.margin.only(bottom=10),
                alignment=ft.alignment.center_right
            )
        )

        # Clear input
        message_input.value = ""
        page.update()

        # Send to API
        try:
            response = requests.post(
                "http://127.0.0.1:8000/api/chatbot/api/",
                json={"message": user_message},
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                bot_answer = data.get("answer", "No response")
            else:
                bot_answer = "Error: Could not get response from chatbot."
        except Exception as ex:
            bot_answer = f"Error: {str(ex)}"

        # Add bot response
        chat_history.controls.append(
            ft.Container(
                content=ft.Text(f"Bot: {bot_answer}", color="#000000"),
                bgcolor="#e0e0e0",
                padding=10,
                border_radius=10,
                margin=ft.margin.only(bottom=10),
                alignment=ft.alignment.center_left
            )
        )
        page.update()

    send_button = ft.ElevatedButton(
        "Send",
        on_click=send_message,
        bgcolor=PRIMARY_GREEN,
        color=BUTTON_TEXT,
        width=100
    )

    back_button = ft.ElevatedButton(
        "Back",
        on_click=lambda e: go_back(),
        bgcolor=SECONDARY_GREEN,
        color=BUTTON_TEXT,
        width=100
    )

    page.add(
        ft.Container(
            content=ft.Column(
                [
                    ft.Text("Chatbot", size=24, weight=ft.FontWeight.BOLD, color="#000000"),
                    chat_history,
                    ft.Row([message_input, send_button], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Container(height=20),
                    back_button
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            padding=20,
            alignment=ft.alignment.center
        )
    )