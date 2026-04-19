from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q

from .models import Donation, ClaimRequest
from .serializers import DonationSerializer, ClaimRequestSerializer


class DonationViewSet(viewsets.ModelViewSet):
    serializer_class = DonationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Donation.objects.all().select_related("donor").prefetch_related("claim_requests")
        category = self.request.query_params.get("category")
        status_value = self.request.query_params.get("status")
        donor_filter = self.request.query_params.get("donor")
        user = self.request.user

        if category:
            queryset = queryset.filter(category=category)

        if donor_filter == "me" and user.is_authenticated:
            queryset = queryset.filter(donor=user)

        if status_value:
            queryset = queryset.filter(status=status_value)
        elif user.is_authenticated and getattr(user, "role", "") == "ngo":
            # NGOs should only browse currently available donations
            queryset = queryset.filter(status="pending")

        return queryset.order_by("-id")

    def perform_create(self, serializer):
        if getattr(self.request.user, "role", "") != "donor":
            raise permissions.PermissionDenied("Only donors can create donation posts")
        serializer.save(donor=self.request.user)

    def perform_update(self, serializer):
        donation = self.get_object()
        if donation.donor != self.request.user:
            raise permissions.PermissionDenied("You can only update your own donations")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.donor != self.request.user:
            raise permissions.PermissionDenied("You can only delete your own donations")
        instance.delete()

    @action(detail=True, methods=["post"])
    def claim(self, request, pk=None):
        donation = self.get_object()
        user = request.user

        if getattr(user, "role", "") != "ngo":
            return Response(
                {"error": "Only NGO users can claim donations"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if donation.status != "pending":
            return Response(
                {"error": "This donation is no longer available."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        existing_claim = ClaimRequest.objects.filter(
            donation=donation,
            receiver=user,
        ).exclude(status="rejected").first()

        if existing_claim:
            return Response(
                {"error": "You already submitted a claim for this donation."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        claim_request = ClaimRequest.objects.create(
            donation=donation,
            receiver=user,
            message=request.data.get("message", "").strip(),
        )

        serializer = ClaimRequestSerializer(claim_request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"])
    def claims(self, request, pk=None):
        donation = self.get_object()

        if donation.donor != request.user:
            return Response(
                {"error": "You can only view claims for your own donations"},
                status=status.HTTP_403_FORBIDDEN,
            )

        claims = ClaimRequest.objects.filter(donation=donation).select_related("receiver", "donation")
        serializer = ClaimRequestSerializer(claims, many=True)
        return Response(serializer.data)


class ClaimRequestViewSet(viewsets.ModelViewSet):
    serializer_class = ClaimRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        claim_type = self.request.query_params.get("type")

        queryset = ClaimRequest.objects.filter(
            Q(donation__donor=user) | Q(receiver=user)
        ).select_related("donation", "receiver", "donation__donor").order_by("-id")

        if claim_type == "received":
            queryset = queryset.filter(donation__donor=user)
        elif claim_type == "sent":
            queryset = queryset.filter(receiver=user)

        return queryset

    def destroy(self, request, *args, **kwargs):
        claim = self.get_object()

        allowed_users = {
            claim.donation.donor_id,
            claim.receiver_id,
        }
        if request.user.id not in allowed_users:
            return Response(
                {"error": "You can only delete claim requests linked to your own donation workflow"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if claim.donation.status != "completed":
            return Response(
                {"error": "Claim requests can only be deleted after the donation handoff is completed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.perform_destroy(claim)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        claim = self.get_object()

        if claim.donation.donor != request.user:
            return Response(
                {"error": "You can only accept claims for your own donations"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if claim.status != "pending":
            return Response(
                {"error": "Only pending claims can be accepted"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        claim.status = "accepted"
        claim.date_responded = timezone.now()
        claim.save()

        ClaimRequest.objects.filter(
            donation=claim.donation,
            status="pending",
        ).exclude(id=claim.id).update(
            status="rejected",
            date_responded=timezone.now(),
        )

        claim.donation.status = "claimed"
        claim.donation.save()

        serializer = ClaimRequestSerializer(claim)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        claim = self.get_object()

        if claim.donation.donor != request.user:
            return Response(
                {"error": "You can only reject claims for your own donations"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if claim.status != "pending":
            return Response(
                {"error": "Only pending claims can be rejected"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        claim.status = "rejected"
        claim.date_responded = timezone.now()
        claim.save()

        donation = claim.donation
        has_pending = donation.claim_requests.filter(status="pending").exists()
        has_accepted = donation.claim_requests.filter(status="accepted").exists()

        if not has_pending and not has_accepted and donation.status != "completed":
            donation.status = "pending"
            donation.save()

        serializer = ClaimRequestSerializer(claim)
        return Response(serializer.data)
