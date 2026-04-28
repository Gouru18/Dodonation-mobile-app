from django.db import models
from django.contrib.auth import get_user_model
from donations.models import ClaimRequest

User = get_user_model()

class Meeting(models.Model):
    STATUS_CHOICES = (
        ('online_scheduled', 'Online Meeting Scheduled'),
        ('online_completed', 'Online Meeting Completed'),
        ('location_pinned', 'Physical Meeting Point Pinned'),
        ('physical_completed', 'Physical Meeting Completed'),
        ('cancelled', 'Cancelled'),
    )

    claim_request = models.OneToOneField(ClaimRequest, on_delete=models.CASCADE, related_name='meeting')
    scheduled_time = models.DateTimeField()
    meeting_link = models.URLField(max_length=500, blank=True, null=True)
    google_meet_space_name = models.CharField(max_length=255, blank=True, null=True)
    meeting_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    meeting_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    meeting_address = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='online_scheduled')
    online_meeting_completed_at = models.DateTimeField(null=True, blank=True)
    location_pinned_at = models.DateTimeField(null=True, blank=True)
    physical_meeting_completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-scheduled_time']

    def __str__(self):
        donation_title = self.claim_request.donation.title
        return f"{donation_title} meeting on {self.scheduled_time:%Y-%m-%d %H:%M}"


class DonorRating(models.Model):
    meeting = models.OneToOneField(Meeting, on_delete=models.CASCADE, related_name='donor_rating')
    ngo = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_ratings')
    donor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_ratings')
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Rating {self.rating} for {self.donor} by {self.ngo} (Meeting {self.meeting_id})"
