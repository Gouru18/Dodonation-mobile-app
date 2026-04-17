import requests

BASE_URL = "http://127.0.0.1:8000/api/chatbot"

class ChatbotService:
    @staticmethod
    def send_message(message):
        response = requests.post(
            f"{BASE_URL}/",
            json={"message": message},
            timeout=5
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response", "No response from chatbot")