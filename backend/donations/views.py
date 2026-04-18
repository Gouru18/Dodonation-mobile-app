from rest_framework import viewsets, status, generics, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q

from .models import Donation, ClaimRequest
from .serializers import DonationSerializer, ClaimRequestSerializer, ClaimRequestActionSerializer


class DonationViewSet(viewsets.ModelViewSet):
    serializer_class = DonationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Donation.objects.all().select_related('donor')
        category = self.request.query_params.get('category')
        status_value = self.request.query_params.get('status')
        donor_filter = self.request.query_params.get('donor')

        if category:
            queryset = queryset.filter(category=category)
        if status_value:
            queryset = queryset.filter(status=status_value)
        if donor_filter == 'me' and self.request.user.is_authenticated:
            queryset = queryset.filter(donor=self.request.user)

        return queryset

    def perform_create(self, serializer):
        # Set donor to current user
        serializer.save(donor=self.request.user)

    def perform_update(self, serializer):
        donation = self.get_object()
        # Only donor can update their own donation
        if donation.donor != self.request.user:
            raise permissions.PermissionDenied("You can only update your own donations")
        serializer.save()

    @action(detail=True, methods=['post'])
    def claim(self, request, pk=None):
        """NGO requests to claim a donation"""
        donation = self.get_object()
        
        if request.user.role != 'ngo':
            return Response(
                {'error': 'Only NGO users can claim donations'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check if claim already exists
        existing_claim = ClaimRequest.objects.filter(
            donation=donation,
            receiver=request.user
        ).first()

        if existing_claim:
            return Response(
                {'error': 'You already have a pending claim for this donation'},
                status=status.HTTP_400_BAD_REQUEST
            )

        claim_request = ClaimRequest.objects.create(
            donation=donation,
            receiver=request.user,
            message=request.data.get('message', '')
        )

        serializer = ClaimRequestSerializer(claim_request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def claims(self, request, pk=None):
        """Get all claims for a donation"""
        donation = self.get_object()
        
        if donation.donor != request.user:
            return Response(
                {'error': 'You can only view claims for your own donations'},
                status=status.HTTP_403_FORBIDDEN
            )

        claims = ClaimRequest.objects.filter(donation=donation)
        serializer = ClaimRequestSerializer(claims, many=True)
        return Response(serializer.data)


class ClaimRequestViewSet(viewsets.ModelViewSet):
    serializer_class = ClaimRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        claim_type = self.request.query_params.get('type')
        queryset = ClaimRequest.objects.filter(
            Q(donation__donor=user) | Q(receiver=user)
        ).select_related('donation', 'receiver')

        if claim_type == 'received':
            queryset = queryset.filter(donation__donor=user)
        elif claim_type == 'sent':
            queryset = queryset.filter(receiver=user)

        return queryset

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Donor accepts a claim request"""
        claim = self.get_object()
        
        if claim.donation.donor != request.user:
            return Response(
                {'error': 'You can only accept claims for your own donations'},
                status=status.HTTP_403_FORBIDDEN
            )

        claim.status = 'accepted'
        claim.date_responded = timezone.now()
        claim.save()

        # Update donation status
        claim.donation.status = 'claimed'
        claim.donation.save()

        serializer = ClaimRequestSerializer(claim)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Donor rejects a claim request"""
        claim = self.get_object()
        
        if claim.donation.donor != request.user:
            return Response(
                {'error': 'You can only reject claims for your own donations'},
                status=status.HTTP_403_FORBIDDEN
            )

        claim.status = 'rejected'
        claim.date_responded = timezone.now()
        claim.save()

        serializer = ClaimRequestSerializer(claim)
        return Response(serializer.data)
