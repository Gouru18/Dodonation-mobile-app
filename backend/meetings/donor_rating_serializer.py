from rest_framework import serializers
from .models import DonorRating

class DonorRatingSerializer(serializers.ModelSerializer):
    ngo_details = serializers.SerializerMethodField()
    donor_details = serializers.SerializerMethodField()

    class Meta:
        model = DonorRating
        fields = [
            'id',
            'meeting',
            'ngo',
            'ngo_details',
            'donor',
            'donor_details',
            'rating',
            'comment',
            'created_at',
        ]
        read_only_fields = ['id', 'ngo', 'donor', 'created_at']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

    def _user_details(self, user):
        profile = getattr(user, "ngo_profile", None) or getattr(user, "donor_profile", None)
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "organization_name": getattr(profile, "organization_name", ""),
            "full_name": getattr(profile, "full_name", ""),
        }

    def get_ngo_details(self, obj):
        return self._user_details(obj.ngo)

    def get_donor_details(self, obj):
        return self._user_details(obj.donor)
