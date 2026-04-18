from rest_framework import serializers
from .models import Meeting
from donations.serializers import ClaimRequestSerializer


class MeetingSerializer(serializers.ModelSerializer):
    claim_request = ClaimRequestSerializer(read_only=True)
    donor = serializers.StringRelatedField(source='claim_request.donation.donor', read_only=True)
    ngo = serializers.StringRelatedField(source='claim_request.receiver', read_only=True)
    can_pin_location = serializers.SerializerMethodField()
    ngo_notification = serializers.SerializerMethodField()

    class Meta:
        model = Meeting
        fields = [
            'id', 'claim_request', 'donor', 'ngo', 'scheduled_time',
            'meeting_link', 'google_meet_space_name', 'meeting_latitude',
            'meeting_longitude', 'meeting_address', 'status',
            'online_meeting_completed_at', 'location_pinned_at',
            'physical_meeting_completed_at', 'can_pin_location',
            'ngo_notification', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'claim_request', 'created_at', 'updated_at']

    def create(self, validated_data):
        claim_request = self.context.get('claim_request')
        if claim_request:
            validated_data['claim_request'] = claim_request
        return super().create(validated_data)

    def get_can_pin_location(self, obj):
        return obj.status == 'online_completed'

    def get_ngo_notification(self, obj):
        if obj.status == 'location_pinned' and obj.meeting_address:
            return 'Donor pinned the physical meeting point.'
        if obj.status == 'physical_completed':
            return 'Physical handoff completed.'
        return ''
