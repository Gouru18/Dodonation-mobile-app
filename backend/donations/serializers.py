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
        if obj.status == 'claimed':
            return 'claimed'
        if obj.claim_requests.filter(status='pending').exists():
            return 'pending'
        if obj.claim_requests.filter(status='rejected').exists():
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
