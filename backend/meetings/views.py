from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q

from .models import Meeting
from .serializers import MeetingSerializer
from .google_meet import GoogleMeetError, create_google_meet_space
from donations.models import ClaimRequest


class MeetingViewSet(viewsets.ModelViewSet):
    serializer_class = MeetingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        status_value = self.request.query_params.get('status')
        queryset = Meeting.objects.filter(
            Q(claim_request__donation__donor=user) | Q(claim_request__receiver=user)
        ).select_related('claim_request')

        if status_value:
            queryset = queryset.filter(status=status_value)

        return queryset

    def create(self, request, *args, **kwargs):
        """Donor schedules an online Google Meet after accepting a claim."""
        claim_id = request.data.get('claim_request')
        
        try:
            claim = ClaimRequest.objects.get(id=claim_id, status='accepted')
        except ClaimRequest.DoesNotExist:
            return Response(
                {'error': 'Claim request not found or not accepted'},
                status=status.HTTP_404_NOT_FOUND
            )

        if request.user != claim.donation.donor:
            return Response(
                {'error': 'Only the donor can schedule the Google Meet.'},
                status=status.HTTP_403_FORBIDDEN
            )

        if Meeting.objects.filter(claim_request=claim).exists():
            return Response(
                {'error': 'Meeting already exists for this claim'},
                status=status.HTTP_400_BAD_REQUEST
            )

        scheduled_time = request.data.get('scheduled_time')
        if not scheduled_time:
            return Response(
                {'error': 'scheduled_time is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(
            data={'scheduled_time': scheduled_time},
            context={'claim_request': claim}
        )
        serializer.is_valid(raise_exception=True)

        try:
            meet_space = create_google_meet_space()
        except GoogleMeetError as exc:
            return Response(
                {'error': f'Google Meet scheduling failed: {exc}'},
                status=status.HTTP_502_BAD_GATEWAY
            )
        except Exception:
            return Response(
                {'error': 'Google Meet is not configured. Set Google application credentials for the backend.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        meeting = serializer.save(
            meeting_link=meet_space.get('meeting_uri'),
            google_meet_space_name=meet_space.get('space_name'),
            status='online_scheduled',
        )

        return Response(self.get_serializer(meeting).data, status=status.HTTP_201_CREATED)

    def perform_update(self, serializer):
        meeting = self.get_object()
        if self.request.user != meeting.claim_request.donation.donor:
            raise permissions.PermissionDenied("Only the donor can update this meeting")
        if meeting.status != 'online_scheduled':
            raise permissions.PermissionDenied("Meeting can only be updated before the online meeting is completed")
        serializer.save()

    @action(detail=True, methods=['post'])
    def complete_online(self, request, pk=None):
        """Mark the online Google Meet as completed."""
        meeting = self.get_object()

        if request.user != meeting.claim_request.donation.donor:
            return Response(
                {'error': 'Only the donor can mark the online meeting as completed'},
                status=status.HTTP_403_FORBIDDEN
            )

        if meeting.status != 'online_scheduled':
            return Response(
                {'error': 'Online meeting is not awaiting completion'},
                status=status.HTTP_400_BAD_REQUEST
            )

        meeting.status = 'online_completed'
        meeting.online_meeting_completed_at = timezone.now()
        meeting.save(update_fields=['status', 'online_meeting_completed_at', 'updated_at'])

        serializer = self.get_serializer(meeting)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def pin_location(self, request, pk=None):
        """Pin the physical meeting point after the online meeting is completed."""
        meeting = self.get_object()

        if request.user != meeting.claim_request.donation.donor:
            return Response(
                {'error': 'Only the donor can pin the meeting point'},
                status=status.HTTP_403_FORBIDDEN
            )

        if meeting.status != 'online_completed':
            return Response(
                {'error': 'Complete the online meeting before pinning the physical meeting point'},
                status=status.HTTP_400_BAD_REQUEST
            )

        latitude = request.data.get('meeting_latitude')
        longitude = request.data.get('meeting_longitude')
        address = request.data.get('meeting_address')

        if latitude in (None, '') or longitude in (None, ''):
            return Response(
                {'error': 'meeting_latitude and meeting_longitude are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        meeting.meeting_latitude = latitude
        meeting.meeting_longitude = longitude
        meeting.meeting_address = address
        meeting.location_pinned_at = timezone.now()
        meeting.status = 'location_pinned'
        meeting.save(
            update_fields=[
                'meeting_latitude',
                'meeting_longitude',
                'meeting_address',
                'location_pinned_at',
                'status',
                'updated_at',
            ]
        )

        serializer = self.get_serializer(meeting)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def complete_physical(self, request, pk=None):
        """Mark the physical handoff as completed and clear the map point."""
        meeting = self.get_object()

        if request.user != meeting.claim_request.donation.donor:
            return Response(
                {'error': 'Only the donor can mark the physical meeting as completed'},
                status=status.HTTP_403_FORBIDDEN
            )

        if meeting.status != 'location_pinned':
            return Response(
                {'error': 'Pin the meeting point before completing the physical handoff'},
                status=status.HTTP_400_BAD_REQUEST
            )

        meeting.status = 'physical_completed'
        meeting.physical_meeting_completed_at = timezone.now()
        meeting.meeting_latitude = None
        meeting.meeting_longitude = None
        meeting.meeting_address = None
        meeting.save(
            update_fields=[
                'status',
                'physical_meeting_completed_at',
                'meeting_latitude',
                'meeting_longitude',
                'meeting_address',
                'updated_at',
            ]
        )

        meeting.claim_request.donation.status = 'completed'
        meeting.claim_request.donation.save()

        serializer = self.get_serializer(meeting)
        return Response(serializer.data)
