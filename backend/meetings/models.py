from django.db import models
from django.contrib.auth import get_user_model
from donations.models import ClaimRequest

User = get_user_model()

class Meeting(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    claim_request = models.OneToOneField(ClaimRequest, on_delete=models.CASCADE, related_name='meeting')
    scheduled_time = models.DateTimeField()
    meeting_link = models.URLField(max_length=500, blank=True, null=True)
    meeting_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    meeting_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    meeting_address = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-scheduled_time']

    def __str__(self):
        donation_title = self.claim_request.donation.title
        return f"{donation_title} meeting on {self.scheduled_time:%Y-%m-%d %H:%M}"
