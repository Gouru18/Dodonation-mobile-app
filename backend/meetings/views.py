from rest_framework import viewsets
from django.core.mail import send_mail
from django.conf import settings
from .models import Meeting
from .serializers import MeetingSerializer

class MeetingViewSet(viewsets.ModelViewSet):
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer

    def perform_create(self, serializer):
        # 1. Save the meeting to the database first
        meeting = serializer.save()

        # 2. Prepare the email content
        subject = f"New Meeting Scheduled for Donation: {meeting.donation.title}"
        message = (
            f"Hello,\n\n"
            f"A new meeting has been scheduled between {meeting.donor.username} "
            f"and {meeting.ngo.username} on {meeting.scheduled_time}.\n\n"
            f"Meeting Link: {meeting.meeting_link or 'To be provided'}\n\n"
            f"Thank you,\nThe Dodonation Team"
        )
        
        # 3. Send the email (For now, we'll pretend the user's email is their username + @test.com)
        # Note to Person 1 & 2: Once the custom User model is done, change this to user.email
        recipient_list = [f"{meeting.donor.username}@test.com", f"{meeting.ngo.username}@test.com"]
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )