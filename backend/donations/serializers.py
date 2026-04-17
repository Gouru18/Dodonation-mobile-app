from rest_framework import serializers
from .models import Donation  # <-- This needs to be Donation, not Meeting

class DonationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donation
        fields = '__all__'