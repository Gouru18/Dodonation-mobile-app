import requests
from utils.config import BASE_URL
from services.auth_service import AuthService


class ChatbotService:
    @staticmethod
    def send_message(message):
        """Send message to chatbot and get response"""
        try:
            response = requests.post(
                f"{BASE_URL}/chatbot/",
                json={"message": message},
                headers=AuthService.auth_headers(),
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return data.get("answer", "Sorry, I didn't understand that. Please try again.")
        except requests.exceptions.RequestException as e:
            return f"Error communicating with chatbot: {str(e)}"