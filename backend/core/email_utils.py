from django.core.mail import send_mail
from django.conf import settings
import logging


logger = logging.getLogger(__name__)

EMAIL_PLACEHOLDERS = {
    'your_gmail_address@gmail.com',
    'your_16_character_gmail_app_password',
}


class EmailDeliveryError(Exception):
    """Raised when an email cannot be delivered."""


def _ensure_email_settings_configured():
    if (
        settings.EMAIL_HOST_USER
        and settings.EMAIL_HOST_PASSWORD
        and settings.EMAIL_HOST_USER not in EMAIL_PLACEHOLDERS
        and settings.EMAIL_HOST_PASSWORD not in EMAIL_PLACEHOLDERS
    ):
        return

    raise EmailDeliveryError(
        "Email service is not configured. Set EMAIL_HOST_USER and a Gmail App Password in environment variables."
    )


def send_otp_email(email, otp_code):
    """Send OTP code via email"""
    _ensure_email_settings_configured()

    subject = "Your OTP Code"
    message = (
        f"Hello,\n\n"
        f"Your One-Time Password (OTP) for Dodonation is: {otp_code}\n\n"
        f"This code will expire in 10 minutes.\n"
        f"Do not share this code with anyone.\n\n"
        f"Thank you,\nThe Dodonation Team"
    )
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        return True
    except Exception as exc:
        logger.exception("Failed to send OTP email to %s", email)
        detail = "Failed to send OTP email. Check Gmail App Password and SMTP settings."
        if settings.DEBUG:
            detail = f"{detail} Original error: {exc}"
        raise EmailDeliveryError(detail) from exc


def send_ngo_status_email(email, status, organization_name=None, rejection_reason=None):
    """Send NGO status update email to an NGO."""
    _ensure_email_settings_configured()

    if status == 'approved':
        return send_ngo_approval_email(email, organization_name or '')

    return send_ngo_rejection_email(
        email,
        organization_name or '',
        rejection_reason or 'No reason provided.',
    )


def send_ngo_approval_email(ngo_email, organization_name):
    """Send NGO approval email"""
    subject = f"Your NGO {organization_name} has been approved!"
    message = (
        f"Hello,\n\n"
        f"Great news! Your NGO '{organization_name}' has been approved by the admin.\n"
        f"You can now log in and use the Dodonation app.\n\n"
        f"Username: {ngo_email}\n\n"
        f"Thank you,\nThe Dodonation Team"
    )
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[ngo_email],
            fail_silently=False,
        )
        return True
    except Exception as exc:
        logger.exception("Failed to send NGO approval email to %s", ngo_email)
        raise EmailDeliveryError(
            "Failed to deliver NGO approval email. Check SMTP settings and recipient address."
        ) from exc


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
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[ngo_email],
            fail_silently=False,
        )
        return True
    except Exception as exc:
        logger.exception("Failed to send NGO rejection email to %s", ngo_email)
        raise EmailDeliveryError(
            "Failed to deliver NGO rejection email. Check SMTP settings and recipient address."
        ) from exc


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
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[donor_email],
            fail_silently=False,
        )
        return True
    except Exception:
        logger.exception("Failed to send donation claimed email to %s", donor_email)
        return False


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
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[donor_email, ngo_email],
            fail_silently=False,
        )
        return True
    except Exception:
        logger.exception(
            "Failed to send meeting scheduled email to %s and %s",
            donor_email,
            ngo_email,
        )
        return False
