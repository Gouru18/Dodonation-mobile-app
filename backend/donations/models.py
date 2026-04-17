from django.db import models

class Donation(models.Model):
    # Dummy field so the model isn't empty (Person 1 will add the rest later)
    title = models.CharField(max_length=200, default="Pending Item") 
    
    # [Person 4 Task]: Map Integration - Location tracking
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # ADD THIS LINE for the email trigger logic:
    is_accepted = models.BooleanField(default=False)

    def __str__(self):
        return self.title