from rest_framework import serializers
from .models import ChatbotFAQ

class ChatbotFAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatbotFAQ
        fields = ['id', 'question', 'answer']