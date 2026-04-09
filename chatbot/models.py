from django.db import models

class ChatbotFAQ(models.Model):
    question = models.CharField(max_length=255, unique=True)
    answer = models.TextField()

    def __str__(self):
        return self.question