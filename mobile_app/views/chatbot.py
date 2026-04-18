import asyncio
import flet as ft
from services.chatbot_service import ChatbotService
from utils.constants import PRIMARY_GREEN, SECONDARY_GREEN, BUTTON_TEXT, INPUT_TEXT
from utils.helpers import build_appbar, centered_content, page_container, section_card, show_message

def chatbot_view(page: ft.Page):
    chat_history = ft.ListView(spacing=12, expand=True, auto_scroll=True)
    message_input = ft.TextField(label="Message", expand=True, color=INPUT_TEXT)

    async def send_message(e):
        message = message_input.value.strip()
        if not message:
            show_message(page, "Enter a message first", "red")
            return

        chat_history.controls.append(
            ft.Container(
                content=ft.Text(message, color="#1F2937"),
                bgcolor="#E4F0DF",
                border_radius=16,
                padding=14,
                alignment=ft.Alignment(1, 0),
                width=760,
            )
        )
        message_input.value = ""
        page.update()

        try:
            answer = await asyncio.to_thread(ChatbotService.send_message, message)
            chat_history.controls.append(
                ft.Container(
                    content=ft.Text(answer, color="#1F2937"),
                    bgcolor="#FFFFFF",
                    border=ft.Border.all(1, "#D6E2D3"),
                    border_radius=16,
                    padding=14,
                    width=760,
                )
            )
        except Exception as ex:
            chat_history.controls.append(ft.Text(f"Bot error: {ex}", color="red"))
        page.update()

    async def go_back(e):
        await page.push_route("/dashboard")

    return ft.View(
        route="/chatbot",
        appbar=build_appbar("Chatbot", go_back),
        controls=[
            page_container(
                centered_content(
                    section_card(
                        "Ask Dodonation Assistant",
                        [
                            ft.Text("Ask about donations, meetings, permits, or general app guidance.", color="#4B5563"),
                            ft.Container(
                                content=chat_history,
                                height=460,
                                border=ft.Border.all(1, "#D6E2D3"),
                                border_radius=16,
                                padding=12,
                                bgcolor="#F9FBF7",
                            ),
                            ft.Row(
                                [
                                    message_input,
                                    ft.Button("Send", on_click=send_message, bgcolor=PRIMARY_GREEN, color=BUTTON_TEXT, width=110),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=12,
                            ),
                            ft.Row(
                                [ft.Button("Back", on_click=go_back, bgcolor=SECONDARY_GREEN, color=BUTTON_TEXT, width=140)],
                                alignment=ft.MainAxisAlignment.END,
                            ),
                        ],
                    )
                ),
            ),
        ],
    )
