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
        status_value = self.request.query_params.get('status')
        queryset = Meeting.objects.filter(
            Q(claim_request__donation__donor=user) | Q(claim_request__receiver=user)
        ).select_related('claim_request')

        if status_value:
            queryset = queryset.filter(status=status_value)

        return queryset

    def create(self, request, *args, **kwargs):
        """Create a meeting for an accepted claim"""
        claim_id = request.data.get('claim_request')
        
        try:
            claim = ClaimRequest.objects.get(id=claim_id, status='accepted')
        except ClaimRequest.DoesNotExist:
            return Response(
                {'error': 'Claim request not found or not accepted'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Only donor or NGO of the claim can create meeting
        if request.user not in [claim.donation.donor, claim.receiver]:
            return Response(
                {'error': 'You are not involved in this claim'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check if meeting already exists for this claim
        if Meeting.objects.filter(claim_request=claim).exists():
            return Response(
                {'error': 'Meeting already exists for this claim'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data, context={'claim_request': claim})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_update(self, serializer):
        meeting = self.get_object()
        # Only involved parties can update meeting
        if self.request.user not in [
            meeting.claim_request.donation.donor,
            meeting.claim_request.receiver
        ]:
            raise permissions.PermissionDenied("You are not involved in this meeting")
        serializer.save()

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm meeting"""
        meeting = self.get_object()
        
        if request.user not in [
            meeting.claim_request.donation.donor,
            meeting.claim_request.receiver
        ]:
            return Response(
                {'error': 'You are not involved in this meeting'},
                status=status.HTTP_403_FORBIDDEN
            )

        meeting.status = 'confirmed'
        meeting.save()

        serializer = self.get_serializer(meeting)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark meeting as completed"""
        meeting = self.get_object()
        
        if request.user != meeting.claim_request.donation.donor:
            return Response(
                {'error': 'Only donor can mark meeting as completed'},
                status=status.HTTP_403_FORBIDDEN
            )

        meeting.status = 'completed'
        meeting.save()

        # Update donation status
        meeting.claim_request.donation.status = 'completed'
        meeting.claim_request.donation.save()

        serializer = self.get_serializer(meeting)
        return Response(serializer.data)
