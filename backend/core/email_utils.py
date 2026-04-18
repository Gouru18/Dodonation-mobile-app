from django.core.mail import send_mail
from django.conf import settings


def send_otp_email(email, otp_code):
    """Send OTP code via email"""
    subject = "Your Dodonation OTP Code"
    message = (
        f"Hello,\n\n"
        f"Your One-Time Password (OTP) for Dodonation is: {otp_code}\n\n"
        f"This code will expire in 10 minutes.\n"
        f"Do not share this code with anyone.\n\n"
        f"Thank you,\nThe Dodonation Team"
    )
    
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )


def send_ngo_approval_email(ngo_email, organization_name):
    """Send NGO approval email"""
    subject = f"Your NGO {organization_name} has been approved!"
    message = (
        f"Hello,\n\n"
        f"Great news! Your NGO '{organization_name}' has been approved by the admin.\n"
        f"You can now log in and use the Dodonation app.\n\n"
        f"Log in at: [APP_URL]\n"
        f"Username: {ngo_email}\n\n"
        f"Thank you,\nThe Dodonation Team"
    )
    
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[ngo_email],
        fail_silently=False,
    )


def send_ngo_rejection_email(ngo_email, organization_name, rejection_reason):
    """Send NGO rejection email"""
    subject = f"Your NGO {organization_name} permit has been rejected"
    message = (
        f"Hello,\n\n"
        f"Unfortunately, your NGO permit '{organization_name}' has been rejected.\n"
        f"Reason: {rejection_reason}\n\n"
        f"You can resubmit your permit for review.\n\n"
        f"Thank you,\nThe Dodonation Team"
    )
    
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[ngo_email],
        fail_silently=False,
    )


def send_donation_claimed_email(donor_email, donation_title, ngo_name):
    """Send email when donation is claimed"""
    subject = f"Your donation '{donation_title}' has been claimed!"
    message = (
        f"Hello,\n\n"
        f"Good news! Your donation '{donation_title}' has been claimed by {ngo_name}.\n"
        f"You can now schedule a pickup meeting.\n\n"
        f"Log in to the app to view the meeting details.\n\n"
        f"Thank you,\nThe Dodonation Team"
    )
    
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[donor_email],
        fail_silently=False,
    )


def send_meeting_scheduled_email(donor_email, ngo_email, donation_title, scheduled_time):
    """Send email when meeting is scheduled"""
    subject = f"Meeting scheduled for donation '{donation_title}'"
    message = (
        f"Hello,\n\n"
        f"A meeting has been scheduled for the donation '{donation_title}'.\n"
        f"Scheduled Time: {scheduled_time}\n\n"
        f"Please check the app for meeting details and location.\n\n"
        f"Thank you,\nThe Dodonation Team"
    )
    
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[donor_email, ngo_email],
        fail_silently=False,
    )
