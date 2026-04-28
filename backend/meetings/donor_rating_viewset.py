from rest_framework import mixins, viewsets, permissions, status
from rest_framework.response import Response
from django.db.models import Q

from .models import DonorRating
from .donor_rating_serializer import DonorRatingSerializer
from meetings.models import Meeting

class DonorRatingViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = DonorRating.objects.all()
    serializer_class = DonorRatingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return DonorRating.objects.filter(
            Q(ngo=user) | Q(donor=user)
        ).select_related(
            "meeting",
            "ngo",
            "ngo__ngo_profile",
            "donor",
            "donor__donor_profile",
        )

    def create(self, request, *args, **kwargs):
        user = request.user
        meeting_id = request.data.get('meeting')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rating = serializer.validated_data["rating"]
        comment = request.data.get('comment', '')

        try:
            meeting = Meeting.objects.select_related(
                "claim_request",
                "claim_request__receiver",
                "claim_request__donation",
                "claim_request__donation__donor",
            ).get(id=meeting_id)
        except Meeting.DoesNotExist:
            return Response({'error': 'Meeting not found.'}, status=status.HTTP_404_NOT_FOUND)

        if meeting.status != 'physical_completed':
            return Response({'error': 'Can only rate after physical meeting is completed.'}, status=status.HTTP_400_BAD_REQUEST)

        if meeting.claim_request.receiver != user:
            return Response({'error': 'Only the NGO can rate the donor.'}, status=status.HTTP_403_FORBIDDEN)

        if DonorRating.objects.filter(meeting=meeting).exists():
            return Response({'error': 'You have already rated this donor for this meeting.'}, status=status.HTTP_400_BAD_REQUEST)

        if meeting.claim_request.donation.donor == user:
            return Response({'error': 'Self-rating is not allowed.'}, status=status.HTTP_400_BAD_REQUEST)

        donor_rating = DonorRating.objects.create(
            meeting=meeting,
            ngo=user,
            donor=meeting.claim_request.donation.donor,
            rating=rating,
            comment=comment
        )
        serializer = self.get_serializer(donor_rating)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
