from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q
from django.utils import timezone

from accounts.models import User, OTPCode
from chatbot.models import ChatbotFAQ
from donations.models import Donation, ClaimRequest
from meetings.models import Meeting
from profiles.models import DonorProfile, NGOProfile, NGOPermitApplication

from .serializers import (
    AdminChatbotFAQSerializer,
    AdminClaimRequestSerializer,
    AdminDonationSerializer,
    AdminDonorProfileSerializer,
    AdminMeetingSerializer,
    AdminNGOPermitSerializer,
    AdminNGOProfileSerializer,
    AdminOTPCodeSerializer,
    AdminUserSerializer,
)


class AdminOnlyMixin:
    permission_classes = [permissions.IsAdminUser]


class AdminDashboardViewSet(AdminOnlyMixin, viewsets.ViewSet):
    def list(self, request):
        return Response(
            {
                'users': {
                    'total': User.objects.count(),
                    'admins': User.objects.filter(Q(is_staff=True) | Q(is_superuser=True)).count(),
                    'donors': User.objects.filter(role='donor').count(),
                    'ngos': User.objects.filter(role='ngo').count(),
                    'active': User.objects.filter(is_active=True).count(),
                },
                'permits': {
                    'pending': NGOPermitApplication.objects.filter(status='pending').count(),
                    'approved': NGOPermitApplication.objects.filter(status='approved').count(),
                    'rejected': NGOPermitApplication.objects.filter(status='rejected').count(),
                },
                'donations': {
                    'total': Donation.objects.count(),
                    'pending': Donation.objects.filter(status='pending').count(),
                    'claimed': Donation.objects.filter(status='claimed').count(),
                    'completed': Donation.objects.filter(status='completed').count(),
                },
                'claims': {
                    'total': ClaimRequest.objects.count(),
                    'pending': ClaimRequest.objects.filter(status='pending').count(),
                    'accepted': ClaimRequest.objects.filter(status='accepted').count(),
                    'rejected': ClaimRequest.objects.filter(status='rejected').count(),
                },
                'meetings': {
                    'total': Meeting.objects.count(),
                    'active': Meeting.objects.exclude(status='physical_completed').exclude(status='cancelled').count(),
                },
                'faqs': ChatbotFAQ.objects.count(),
                'otp_codes': OTPCode.objects.count(),
            }
        )


class AdminUserViewSet(AdminOnlyMixin, viewsets.ModelViewSet):
    serializer_class = AdminUserSerializer
    queryset = User.objects.all().select_related('ngo_profile__permit_application')

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.query_params.get('q')
        role = self.request.query_params.get('role')
        is_active = self.request.query_params.get('is_active')

        if q:
            queryset = queryset.filter(Q(username__icontains=q) | Q(email__icontains=q))
        if role:
            if role == 'admin':
                queryset = queryset.filter(Q(role='admin') | Q(is_staff=True) | Q(is_superuser=True))
            else:
                queryset = queryset.filter(role=role)
        if is_active in {'true', 'false'}:
            queryset = queryset.filter(is_active=is_active == 'true')
        return queryset.order_by('username', 'email')

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        user = self.get_object()
        user.is_active = True
        user.save(update_fields=['is_active'])
        return Response(self.get_serializer(user).data)

    @action(detail=True, methods=['post'])
    def suspend(self, request, pk=None):
        user = self.get_object()
        user.is_active = False
        user.save(update_fields=['is_active'])
        return Response(self.get_serializer(user).data)


class AdminOTPCodeViewSet(AdminOnlyMixin, viewsets.ModelViewSet):
    serializer_class = AdminOTPCodeSerializer
    queryset = OTPCode.objects.all().select_related('user')

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.query_params.get('q')
        if q:
            queryset = queryset.filter(user__email__icontains=q)
        return queryset.order_by('-created_at')


class AdminDonorProfileViewSet(AdminOnlyMixin, viewsets.ModelViewSet):
    serializer_class = AdminDonorProfileSerializer
    queryset = DonorProfile.objects.all().select_related('user')

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.query_params.get('q')
        if q:
            queryset = queryset.filter(Q(full_name__icontains=q) | Q(user__email__icontains=q))
        return queryset.order_by('full_name')


class AdminNGOProfileViewSet(AdminOnlyMixin, viewsets.ModelViewSet):
    serializer_class = AdminNGOProfileSerializer
    queryset = NGOProfile.objects.all().select_related('user', 'permit_application')

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.query_params.get('q')
        if q:
            queryset = queryset.filter(Q(organization_name__icontains=q) | Q(user__email__icontains=q))
        return queryset.order_by('organization_name')


class AdminNGOPermitViewSet(AdminOnlyMixin, viewsets.ModelViewSet):
    serializer_class = AdminNGOPermitSerializer
    queryset = NGOPermitApplication.objects.all().select_related('ngo__user', 'reviewed_by')

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.query_params.get('q')
        status_value = self.request.query_params.get('status')
        if q:
            queryset = queryset.filter(ngo__organization_name__icontains=q)
        if status_value:
            queryset = queryset.filter(status=status_value)
        return queryset.order_by('-submitted_at')

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        permit = self.get_object()
        permit.status = 'approved'
        permit.reviewed_by = request.user
        permit.reviewed_at = timezone.now()
        permit.rejection_reason = ''
        permit.save()
        permit.ngo.user.is_active = True
        permit.ngo.user.save(update_fields=['is_active'])
        return Response(self.get_serializer(permit).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        permit = self.get_object()
        permit.status = 'rejected'
        permit.reviewed_by = request.user
        permit.reviewed_at = timezone.now()
        permit.rejection_reason = request.data.get('rejection_reason', '')
        permit.save()
        return Response(self.get_serializer(permit).data)


class AdminDonationViewSet(AdminOnlyMixin, viewsets.ModelViewSet):
    serializer_class = AdminDonationSerializer
    queryset = Donation.objects.all().select_related('donor')

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.query_params.get('q')
        status_value = self.request.query_params.get('status')
        category = self.request.query_params.get('category')
        if q:
            queryset = queryset.filter(Q(title__icontains=q) | Q(donor__email__icontains=q))
        if status_value:
            queryset = queryset.filter(status=status_value)
        if category:
            queryset = queryset.filter(category=category)
        return queryset.order_by('-created_at')


class AdminClaimRequestViewSet(AdminOnlyMixin, viewsets.ModelViewSet):
    serializer_class = AdminClaimRequestSerializer
    queryset = ClaimRequest.objects.all().select_related('donation__donor', 'receiver')

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.query_params.get('q')
        status_value = self.request.query_params.get('status')
        if q:
            queryset = queryset.filter(Q(donation__title__icontains=q) | Q(receiver__email__icontains=q))
        if status_value:
            queryset = queryset.filter(status=status_value)
        return queryset.order_by('-date_requested')

    def create(self, request, *args, **kwargs):
        return Response(
            {'detail': 'Admin can edit or delete claim requests, but cannot create them.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def perform_update(self, serializer):
        instance = serializer.save()
        if instance.status in {'accepted', 'rejected'} and not instance.date_responded:
            instance.date_responded = timezone.now()
            instance.save(update_fields=['date_responded'])
        if instance.status == 'accepted' and instance.donation.status != 'claimed':
            instance.donation.status = 'claimed'
            instance.donation.save(update_fields=['status'])


class AdminMeetingViewSet(AdminOnlyMixin, viewsets.ModelViewSet):
    serializer_class = AdminMeetingSerializer
    queryset = Meeting.objects.all().select_related('claim_request__donation__donor', 'claim_request__receiver')

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.query_params.get('q')
        status_value = self.request.query_params.get('status')
        if q:
            queryset = queryset.filter(
                Q(claim_request__donation__title__icontains=q) |
                Q(claim_request__receiver__email__icontains=q) |
                Q(claim_request__donation__donor__email__icontains=q)
            )
        if status_value:
            queryset = queryset.filter(status=status_value)
        return queryset.order_by('-scheduled_time')


class AdminChatbotFAQViewSet(AdminOnlyMixin, viewsets.ModelViewSet):
    serializer_class = AdminChatbotFAQSerializer
    queryset = ChatbotFAQ.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.query_params.get('q')
        if q:
            queryset = queryset.filter(question__icontains=q)
        return queryset.order_by('question')
