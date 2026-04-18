from rest_framework import serializers
from .models import Donation, ClaimRequest
from accounts.serializers import UserSerializer


class DonationSerializer(serializers.ModelSerializer):
    donor = UserSerializer(read_only=True)

    class Meta:
        model = Donation
        fields = [
            'id', 'donor', 'title', 'description', 'category', 'quantity',
            'expiry_date', 'latitude', 'longitude', 'status', 'image',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'donor', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['donor'] = self.context['request'].user
        return super().create(validated_data)


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