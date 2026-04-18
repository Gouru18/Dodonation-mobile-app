from rest_framework import serializers
from .models import Meeting
from donations.serializers import ClaimRequestSerializer


class MeetingSerializer(serializers.ModelSerializer):
    claim_request = ClaimRequestSerializer(read_only=True)
    donor = serializers.StringRelatedField(source='claim_request.donation.donor', read_only=True)
    ngo = serializers.StringRelatedField(source='claim_request.receiver', read_only=True)

    class Meta:
        model = Meeting
        fields = [
            'id', 'claim_request', 'donor', 'ngo', 'scheduled_time',
            'meeting_link', 'meeting_latitude', 'meeting_longitude',
            'meeting_address', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'claim_request', 'created_at', 'updated_at']

    def create(self, validated_data):
        claim_request = self.context.get('claim_request')
        if claim_request:
            validated_data['claim_request'] = claim_request
        return super().create(validated_data)