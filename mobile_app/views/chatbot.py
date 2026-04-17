import flet as ft
from services.chatbot_service import ChatbotService
from utils.constants import PRIMARY_GREEN, SECONDARY_GREEN, BUTTON_TEXT, INPUT_TEXT
from utils.helpers import show_message


def chatbot_view(page: ft.Page):
    chat_history = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
    message_input = ft.TextField(label="Message", expand=True, color=INPUT_TEXT)

    def send_message(e):
        message = message_input.value.strip()
        if not message:
            show_message(page, "Enter a message first", "red")
            return

        chat_history.controls.append(ft.Text(f"You: {message}", color=INPUT_TEXT))
        message_input.value = ""
        page.update()

        try:
            answer = ChatbotService.send_message(message)
            chat_history.controls.append(ft.Text(f"Bot: {answer}", color="#444"))
        except Exception as ex:
            chat_history.controls.append(ft.Text(f"Bot error: {ex}", color="red"))
        page.update()

    return ft.View(
        route="/chatbot",
        appbar=ft.AppBar(title=ft.Text("Donation App - Chatbot")),
        controls=[
            ft.Container(
                expand=True,
                padding=20,
                content=ft.Column(
                    [
                        chat_history,
                        ft.Row([message_input, ft.ElevatedButton("Send", on_click=send_message, bgcolor=PRIMARY_GREEN, color=BUTTON_TEXT)], alignment=ft.MainAxisAlignment.CENTER),
                        ft.ElevatedButton("Back", on_click=lambda e: page.go("/dashboard"), bgcolor=SECONDARY_GREEN, color=BUTTON_TEXT),
                    ],
                    spacing=15,
                ),
            )
        ],
    )
