from django.conf import settings
from django.db import models

class DonorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.full_name
    
    class NGOProfile(models.Model):
        user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
        organization_name = models.CharField(max_length=255)
        registration_number = models.CharField(max_length=100, blank=True, null=True)
        address = models.TextField(blank=True, null=True)

        def __str__(self):
            return self.organization_name