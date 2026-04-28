from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q

from .models import Meeting
from .serializers import MeetingSerializer
from donations.models import ClaimRequest


class MeetingViewSet(viewsets.ModelViewSet):
    serializer_class = MeetingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        status_value = self.request.query_params.get("status")

        queryset = Meeting.objects.filter(
            Q(claim_request__donation__donor=user) |
            Q(claim_request__receiver=user)
        ).select_related(
            "claim_request",
            "claim_request__donation",
            "claim_request__receiver",
            "claim_request__donation__donor",
            "donor_rating",
            "donor_rating__ngo__ngo_profile",
            "donor_rating__donor__donor_profile",
        ).order_by("-scheduled_time")

        if status_value:
            queryset = queryset.filter(status=status_value)

        return queryset

    def create(self, request, *args, **kwargs):
        if getattr(request.user, "role", "") != "donor":
            return Response(
                {"error": "Only donors can schedule meetings."},
                status=status.HTTP_403_FORBIDDEN
            )

        claim_id = request.data.get("claim_request")
        scheduled_time = request.data.get("scheduled_time")
        meeting_link = request.data.get("meeting_link")

        if not claim_id or not scheduled_time or not meeting_link:
            return Response(
                {"error": "claim_request, scheduled_time, and meeting_link are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if "meet.google.com" not in str(meeting_link).lower():
            return Response(
                {"error": "Please provide a valid Google Meet link."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            claim = ClaimRequest.objects.get(id=claim_id, status="accepted")
        except ClaimRequest.DoesNotExist:
            return Response(
                {"error": "Claim request not found or not accepted."},
                status=status.HTTP_404_NOT_FOUND
            )

        if request.user != claim.donation.donor:
            return Response(
                {"error": "Only the donor can schedule the meeting."},
                status=status.HTTP_403_FORBIDDEN
            )

        if Meeting.objects.filter(claim_request=claim).exists():
            return Response(
                {"error": "Meeting already exists for this claim."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data={
            "claim_request": claim.id,
            "scheduled_time": scheduled_time,
            "meeting_link": meeting_link,
            "status": "online_scheduled",
        })
        serializer.is_valid(raise_exception=True)
        meeting = serializer.save()

        return Response(
            self.get_serializer(meeting).data,
            status=status.HTTP_201_CREATED
        )

    def perform_update(self, serializer):
        meeting = self.get_object()

        if self.request.user != meeting.claim_request.donation.donor:
            raise permissions.PermissionDenied(
                "Only the donor can update this meeting."
            )

        if meeting.status not in ["online_scheduled", "expired"]:
            raise permissions.PermissionDenied(
                "Meeting can only be rescheduled before the online meeting is completed."
            )

        serializer.save(status="online_scheduled")

    @action(detail=True, methods=["post"])
    def complete_online(self, request, pk=None):
        meeting = self.get_object()

        if request.user != meeting.claim_request.donation.donor:
            return Response(
                {"error": "Only the donor can mark the online meeting as completed."},
                status=status.HTTP_403_FORBIDDEN
            )

        if meeting.status != "online_scheduled":
            return Response(
                {
                    "error": "Online meeting is not awaiting completion.",
                    "current_status": meeting.status,
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        meeting.status = "online_completed"
        meeting.online_meeting_completed_at = timezone.now()
        meeting.save(
            update_fields=[
                "status",
                "online_meeting_completed_at",
                "updated_at",
            ]
        )

        return Response(self.get_serializer(meeting).data)

    @action(detail=True, methods=["post"])
    def pin_location(self, request, pk=None):
        meeting = self.get_object()

        allowed_users = {
            meeting.claim_request.donation.donor_id,
            meeting.claim_request.receiver_id,
        }

        if request.user.id not in allowed_users:
            return Response(
                {"error": "Only the donor or NGO linked to this meeting can pin the meeting point."},
                status=status.HTTP_403_FORBIDDEN
            )

        if meeting.status != "online_completed":
            return Response(
                {
                    "error": "Complete the online meeting before pinning the physical meeting point.",
                    "current_status": meeting.status,
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        latitude = request.data.get("meeting_latitude")
        longitude = request.data.get("meeting_longitude")
        address = request.data.get("meeting_address", "")

        if latitude in (None, "") or longitude in (None, ""):
            return Response(
                {"error": "meeting_latitude and meeting_longitude are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        meeting.meeting_latitude = latitude
        meeting.meeting_longitude = longitude
        meeting.meeting_address = address
        meeting.location_pinned_at = timezone.now()
        meeting.status = "location_pinned"

        meeting.save(
            update_fields=[
                "meeting_latitude",
                "meeting_longitude",
                "meeting_address",
                "location_pinned_at",
                "status",
                "updated_at",
            ]
        )

        return Response(self.get_serializer(meeting).data)

    @action(detail=True, methods=["post"])
    def complete_physical(self, request, pk=None):
        meeting = self.get_object()

        if request.user != meeting.claim_request.donation.donor:
            return Response(
                {"error": "Only the donor can mark the physical meeting as completed."},
                status=status.HTTP_403_FORBIDDEN
            )

        if meeting.status != "location_pinned":
            return Response(
                {
                    "error": "Pin the meeting point before completing the physical handoff.",
                    "current_status": meeting.status,
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        meeting.status = "physical_completed"
        meeting.physical_meeting_completed_at = timezone.now()
        meeting.save(
            update_fields=[
                "status",
                "physical_meeting_completed_at",
                "updated_at",
            ]
        )

        donation = meeting.claim_request.donation
        donation.status = "completed"
        donation.save(update_fields=["status"])

        return Response(self.get_serializer(meeting).data)
