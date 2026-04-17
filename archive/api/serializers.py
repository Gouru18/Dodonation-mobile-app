from rest_framework import serializers
from archive.core.models import Donation
from archive.core.models import ClaimRequest
from archive.core.models import GeneralReview
from archive.core.models import Report
from archive.users.models import User
from archive.ngo.models import NGOProfile
from archive.donor.models import DonorProfile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']

class DonationSerializer(serializers.ModelSerializer):
    donor_username = serializers.CharField(source='donor.user.username', read_only=True)

    class Meta:
        model = Donation
        fields = ['id', 'title', 'description', 'quantity', 'expiry_date', 'status', 'donor_username']

class ClaimRequestSerializer(serializers.ModelSerializer):
    donation_title = serializers.CharField(source='donation.title', read_only=True)
    receiver_name = serializers.CharField(source='receiver.user.username', read_only=True)

    class Meta:
        model = ClaimRequest
        fields = ['id', 'donation_title', 'receiver_name', 'status', 'date_requested']

class GeneralReviewSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = GeneralReview
        fields = ['id', 'user_username', 'name', 'email', 'message', 'created_at']

class ReportSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Report
        fields = ['id', 'user_username', 'name', 'email', 'message', 'created_at']

class NGOProfileSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = NGOProfile
        fields = [
            'id',
            'user_username',
            'name',
            'reg_number',
            'permit_file',
            'verification_status',
            'verified_at'
        ]
    
class DonorProfileSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = DonorProfile
        fields = ['id', 'user_username', 'name', 'description', 'contact_email']