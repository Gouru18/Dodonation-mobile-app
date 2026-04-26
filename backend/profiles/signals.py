from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from core.email_utils import send_ngo_status_email
from .models import NGOPermitApplication


@receiver(pre_save, sender=NGOPermitApplication)
def _store_previous_ngo_permit_status(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        existing = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    instance._previous_status = existing.status


@receiver(post_save, sender=NGOPermitApplication)
def ngo_status_change(sender, instance, created, **kwargs):
    if created:
        return

    previous_status = getattr(instance, '_previous_status', None)
    if previous_status == instance.status:
        return

    ngo_email = instance.ngo.user.email
    organization_name = instance.ngo.organization_name
    status = instance.status
    rejection_reason = getattr(instance, 'rejection_reason', None)

    if status == 'approved':
        send_ngo_status_email(ngo_email, 'approved', organization_name)
    elif status == 'rejected':
        send_ngo_status_email(ngo_email, 'rejected', organization_name, rejection_reason)
