from django.db import models
from archive.users.models import User
from django.utils import timezone

class NGOProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="ngo_profile")
    receiverID = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    reg_number = models.CharField(max_length=50, unique=True)

    
    permit_file = models.FileField(upload_to='ngo_permits/', null=True, blank=True)
    verification_status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
        default='pending'
    )
    verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"NGO: {self.name}"