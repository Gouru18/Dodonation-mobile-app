from django.db import models
from django.contrib.auth import get_user_model
from donations.models import Donation # Importing the model we just made

User = get_user_model()

class Meeting(models.Model):
   
    donation = models.ForeignKey(Donation, on_delete=models.CASCADE, related_name='meetings')
    
    # For now, we use default Django User model. 
    # If Person 1 makes a custom User model later, they will update these foreign keys.
    donor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='donor_meetings')
    ngo = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ngo_meetings')
    
    scheduled_time = models.DateTimeField()
    meeting_link = models.URLField(max_length=500, blank=True, null=True)
    is_accepted = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Meeting at {self.scheduled_time}"