from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import ChatbotFAQ

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chatbot_api(request):
    user_message = request.data.get("message", "").strip().lower()

    if not user_message:
        return Response({"answer": "Please enter a message."})

    faqs = ChatbotFAQ.objects.all()
    best_match = None
    highest_score = 0

    # Keyword-based matching
    for faq in faqs:
        keywords = faq.question.lower().split()
        score = sum(1 for word in keywords if word in user_message)

        if score > highest_score:
            highest_score = score
            best_match = faq

    if best_match and highest_score > 0:
        answer = best_match.answer
    else:
        answer = "Sorry, I don't understand that question. Please try another one. You can ask about donations, meetings, permits, or other donation-related topics."

    return Response({"answer": answer})