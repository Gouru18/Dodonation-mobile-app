from rest_framework import serializers
from .models import Donation, ClaimRequest
from accounts.serializers import UserSerializer


class DonationSerializer(serializers.ModelSerializer):
    donor = UserSerializer(read_only=True)
    feed_status = serializers.SerializerMethodField()

    class Meta:
        model = Donation
        fields = [
            'id', 'donor', 'title', 'description', 'category', 'quantity',
            'expiry_date', 'latitude', 'longitude', 'status', 'feed_status', 'image',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'donor', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['donor'] = self.context['request'].user
        return super().create(validated_data)

    def get_feed_status(self, obj):
        """
        User-friendly status for the mobile feed.

        Underlying workflow is kept unchanged:
        - donation.status='pending' still means the post is open/available
        - donation.status='claimed' means a claim was accepted

        feed_status is what the donor sees in the app:
        - available: open post with no pending/recent rejected claim
        - pending: at least one claim request is waiting
        - claimed: donation has been accepted/closed
        - rejected: the latest handled request was rejected and there are no pending ones
        """
        if obj.status == 'claimed':
            return 'claimed'

        if obj.claim_requests.filter(status='pending').exists():
            return 'pending'

        latest_handled_claim = obj.claim_requests.exclude(status='pending').order_by('-date_requested').first()
        if latest_handled_claim and latest_handled_claim.status == 'rejected':
            return 'rejected'

        if obj.status in {'expired', 'completed'}:
            return obj.status

        return 'available'


class ClaimRequestSerializer(serializers.ModelSerializer):
    donation = DonationSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)

    class Meta:
        model = ClaimRequest
        fields = ['id', 'donation', 'receiver', 'status', 'message', 'date_requested', 'date_responded']
        read_only_fields = ['id', 'receiver', 'date_requested', 'date_responded']

    def create(self, validated_data):
        validated_data['receiver'] = self.context['request'].user
        return super().create(validated_data)


class ClaimRequestActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClaimRequest
        fields = ['status']