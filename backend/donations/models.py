from django.db import models
from django.conf import settings

class Donation(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('claimed', 'Claimed'),
        ('completed', 'Completed'),
        ('expired', 'Expired'),
    )

    CATEGORY_CHOICES = (
        ('food', 'Food'),
        ('clothing', 'Clothing'),
        ('medical', 'Medical'),
        ('books', 'Books'),
        ('furniture', 'Furniture'),
        ('electronics', 'Electronics'),
        ('other', 'Other'),
    )

    donor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='donations')
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    quantity = models.IntegerField(default=1)
    expiry_date = models.DateField(null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    image = models.ImageField(upload_to='donations/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        donor_label = self.donor.email or self.donor.username or f"User #{self.donor_id}"
        return f"{self.title} ({donor_label})"


class ClaimRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )

    donation = models.ForeignKey(Donation, on_delete=models.CASCADE, related_name='claim_requests')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='claim_requests')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    message = models.TextField(blank=True, null=True)
    date_requested = models.DateTimeField(auto_now_add=True)
    date_responded = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-date_requested']
        unique_together = ('donation', 'receiver')

    def __str__(self):
        receiver_label = self.receiver.email or self.receiver.username or f"User #{self.receiver_id}"
        return f"{self.donation.title} -> {receiver_label} [{self.get_status_display()}]"
