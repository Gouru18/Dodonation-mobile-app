from rest_framework import serializers
from django.utils import timezone
from .models import Meeting
from donations.models import ClaimRequest
from donations.serializers import ClaimRequestSerializer
from .donor_rating_serializer import DonorRatingSerializer


class MeetingSerializer(serializers.ModelSerializer):
    claim_request = serializers.PrimaryKeyRelatedField(
        queryset=ClaimRequest.objects.all(),
        write_only=True
    )
    claim_request_data = ClaimRequestSerializer(source="claim_request", read_only=True)

    donor = serializers.StringRelatedField(source='claim_request.donation.donor', read_only=True)
    ngo = serializers.StringRelatedField(source='claim_request.receiver', read_only=True)
    can_pin_location = serializers.SerializerMethodField()
    is_online_expired = serializers.SerializerMethodField()
    display_status = serializers.SerializerMethodField()
    ngo_notification = serializers.SerializerMethodField()
    donor_rating = DonorRatingSerializer(read_only=True)
    can_rate_donor = serializers.SerializerMethodField()

    class Meta:
        model = Meeting
        fields = [
            'id',
            'claim_request',
            'claim_request_data',
            'donor',
            'ngo',
            'scheduled_time',
            'meeting_link',
            'google_meet_space_name',
            'meeting_latitude',
            'meeting_longitude',
            'meeting_address',
            'status',
            'online_meeting_completed_at',
            'location_pinned_at',
            'physical_meeting_completed_at',
            'can_pin_location',
            'is_online_expired',
            'display_status',
            'ngo_notification',
            'donor_rating',
            'can_rate_donor',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'google_meet_space_name',
            'online_meeting_completed_at',
            'location_pinned_at',
            'physical_meeting_completed_at',
            'created_at',
            'updated_at',
        ]

    def get_can_pin_location(self, obj):
        return obj.status == 'online_completed'

    def validate_scheduled_time(self, value):
        if value < timezone.now().replace(second=0, microsecond=0):
            raise serializers.ValidationError("Scheduled time cannot be in the past.")
        return value

    def validate_meeting_link(self, value):
        if value and "meet.google.com" not in str(value).lower():
            raise serializers.ValidationError("Please provide a valid Google Meet link.")
        return value

    def get_is_online_expired(self, obj):
        return (
            obj.status == 'online_scheduled'
            and obj.scheduled_time is not None
            and obj.scheduled_time < timezone.now()
        )

    def get_display_status(self, obj):
        if self.get_is_online_expired(obj):
            return 'expired'
        return obj.status

    def get_ngo_notification(self, obj):
        if self.get_is_online_expired(obj):
            return 'This online meeting time has passed. The donor needs to schedule a new meeting link.'
        if obj.status == 'online_completed':
            return 'Online meeting completed. Donor or NGO can now pin the physical meeting point.'
        if obj.status == 'location_pinned' and obj.meeting_address:
            return 'The physical meeting point has been pinned.'
        if obj.status == 'physical_completed':
            return 'Physical handoff completed.'
        return ''

    def get_can_rate_donor(self, obj):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return False
        return (
            obj.status == 'physical_completed'
            and obj.claim_request.receiver_id == user.id
            and not hasattr(obj, 'donor_rating')
        )
