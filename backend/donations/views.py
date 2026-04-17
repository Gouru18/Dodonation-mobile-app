
from rest_framework import viewsets
from .models import Donation
from .serializers import DonationSerializer
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import viewsets
import random
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail

class DonationViewSet(viewsets.ModelViewSet):
    queryset = Donation.objects.all()
    serializer_class = DonationSerializer

    def perform_update(self, serializer):
        # 1. Get the original donation before it gets saved/updated
        original_instance = self.get_object()
        
        # 2. Save the new updates to the database
        updated_instance = serializer.save()

        # 3. Check if 'is_accepted' was changed from False to True
        if updated_instance.is_accepted and not original_instance.is_accepted:
            subject = f"Update: Your Donation '{updated_instance.title}' was Accepted!"
            message = (
                # CHANGED: Removed the .donor.username lookup
                f"Hello there,\n\n" 
                f"Great news! Your donation request has been accepted by an NGO.\n"
                f"Please check the app to schedule a pickup meeting.\n\n"
                f"Thank you,\nThe Dodonation Team"
            )
            
            # Send the email to the terminal
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                # CHANGED: Hardcoded a test email address for now
                recipient_list=["testdonor@dodonation.com"], 
                fail_silently=False,
            )
            
class RequestOTPView(APIView):
    def post(self, request):
        email = request.data.get('email')
        
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Generate a random 6-digit OTP
        otp_code = str(random.randint(100000, 999999))

        # 2. Prepare the email
        subject = "Your Dodonation OTP Code"
        message = (
            f"Hello,\n\n"
            f"Your One-Time Password (OTP) for Dodonation is: {otp_code}\n\n"
            f"Do not share this code with anyone.\n"
            f"The Dodonation Team"
        )

        # 3. Send the email to the terminal
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            return Response({"message": "OTP sent successfully! Check terminal."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)