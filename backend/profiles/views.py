from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone

from .models import DonorProfile, NGOProfile, NGOPermitApplication
from .serializers import (
    DonorProfileSerializer, NGOProfileSerializer, 
    NGOPermitApplicationSerializer, NGOPermitUploadSerializer, NGOPermitApprovalSerializer
)


class DonorProfileDetailView(generics.RetrieveUpdateAPIView):
    queryset = DonorProfile.objects.all()
    serializer_class = DonorProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.donor_profile


class NGOProfileDetailView(generics.RetrieveUpdateAPIView):
    queryset = NGOProfile.objects.all()
    serializer_class = NGOProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.ngo_profile


class NGOPermitUploadView(generics.CreateAPIView):
    serializer_class = NGOPermitUploadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def create(self, request, *args, **kwargs):
        if request.user.role != 'ngo':
            return Response(
                {'error': 'Only NGO users can upload permits'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().create(request, *args, **kwargs)


class NGOPermitListView(generics.ListAPIView):
    serializer_class = NGOPermitApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            # Admin sees all pending permits
            return NGOPermitApplication.objects.filter(status='pending')
        else:
            # NGO sees their own permit
            try:
                return NGOPermitApplication.objects.filter(ngo=user.ngo_profile)
            except:
                return NGOPermitApplication.objects.none()


class NGOPermitApprovalView(generics.UpdateAPIView):
    queryset = NGOPermitApplication.objects.all()
    serializer_class = NGOPermitApprovalSerializer
    permission_classes = [permissions.IsAdminUser]

    def update(self, request, *args, **kwargs):
        permit = self.get_object()
        status_action = request.data.get('status')

        if status_action == 'approved':
            permit.status = 'approved'
            permit.reviewed_by = request.user
            permit.reviewed_at = timezone.now()
            permit.save()
            
            # Activate the NGO user
            permit.ngo.user.is_active = True
            permit.ngo.user.save()
            
            # TODO: Send approval email to NGO
            return Response(
                {'message': 'Permit approved. NGO user activated.'},
                status=status.HTTP_200_OK
            )
        
        elif status_action == 'rejected':
            permit.status = 'rejected'
            permit.reviewed_by = request.user
            permit.reviewed_at = timezone.now()
            permit.rejection_reason = request.data.get('rejection_reason', '')
            permit.save()
            
            # TODO: Send rejection email to NGO
            return Response(
                {'message': 'Permit rejected.'},
                status=status.HTTP_200_OK
            )
        
        return Response(
            {'error': 'Invalid status'},
            status=status.HTTP_400_BAD_REQUEST
        )
