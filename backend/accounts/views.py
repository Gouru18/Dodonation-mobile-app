from rest_framework import generics, serializers, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
import random

from .serializers import RegisterDonorSerializer, RegisterNGOSerializer, LoginSerializer, UserSerializer
from .models import OTPCode
from core.email_utils import EmailDeliveryError, send_otp_email

User = get_user_model()


def _flatten_serializer_errors(errors):
    """Convert DRF serializer errors into a short readable message."""
    if isinstance(errors, list):
        return " ".join(str(item) for item in errors)
    if isinstance(errors, dict):
        parts = []
        for field, value in errors.items():
            label = "Error" if field == "non_field_errors" else field.replace("_", " ").capitalize()
            parts.append(f"{label}: {_flatten_serializer_errors(value)}")
        return " | ".join(parts)
    return str(errors)


def _friendly_integrity_error_message(exc):
    message = str(exc).lower()
    if 'accounts_user.username' in message:
        return 'A user with this username already exists.'
    if 'accounts_user.email' in message:
        return 'A user with this email already exists.'
    return 'Could not complete registration because this account already exists.'


class RegisterDonorView(generics.CreateAPIView):
    serializer_class = RegisterDonorSerializer
    permission_classes = [AllowAny]
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def create(self, request, *args, **kwargs):
        email = (request.data.get('email') or '').strip()
        username = (request.data.get('username') or '').strip()
        existing_user = None

        if email or username:
            query = Q()
            if email:
                query |= Q(email__iexact=email)
            if username:
                query |= Q(username__iexact=username)
            existing_user = User.objects.filter(query).order_by('-id').first()

        if (
            existing_user
            and existing_user.role == 'donor'
            and not existing_user.is_email_verified
        ):
            try:
                with transaction.atomic():
                    code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
                    expires_at = timezone.now() + timedelta(minutes=10)

                    OTPCode.objects.create(
                        user=existing_user,
                        code=code,
                        expires_at=expires_at
                    )

                    send_otp_email(existing_user.email, code)
            except EmailDeliveryError as exc:
                return Response(
                    {'error': str(exc)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            return Response(
                {
                    'message': 'Donor account already exists but is awaiting OTP verification. A new OTP has been sent to your email.',
                    'user': UserSerializer(existing_user).data,
                    'otp_resent': True,
                },
                status=status.HTTP_200_OK,
            )

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    'message': _flatten_serializer_errors(serializer.errors),
                    'errors': serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            self.perform_create(serializer)
        except EmailDeliveryError as exc:
            return Response(
                {
                    'message': str(exc),
                    'errors': {'email': [str(exc)]},
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except serializers.ValidationError as exc:
            detail = exc.detail if hasattr(exc, 'detail') else {'detail': [str(exc)]}
            return Response(
                {
                    'message': _flatten_serializer_errors(detail),
                    'errors': detail,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except IntegrityError as exc:
            return Response(
                {
                    'message': _friendly_integrity_error_message(exc),
                    'errors': {'detail': [_friendly_integrity_error_message(exc)]},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        headers = self.get_success_headers(serializer.data)
        return Response(
            {
                'message': 'Donor registered successfully. OTP sent to email.',
                'user': serializer.data,
            },
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


class RegisterNGOView(generics.CreateAPIView):
    serializer_class = RegisterNGOSerializer
    permission_classes = [AllowAny]
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def create(self, request, *args, **kwargs):
        email = (request.data.get('email') or '').strip()
        username = (request.data.get('username') or '').strip()
        existing_user = None

        if email or username:
            query = Q()
            if email:
                query |= Q(email__iexact=email)
            if username:
                query |= Q(username__iexact=username)
            existing_user = User.objects.filter(query).order_by('-id').first()

        if (
            existing_user
            and existing_user.role == 'ngo'
            and not existing_user.is_active
            and not existing_user.is_email_verified
        ):
            try:
                with transaction.atomic():
                    code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
                    expires_at = timezone.now() + timedelta(minutes=10)

                    OTPCode.objects.create(
                        user=existing_user,
                        code=code,
                        expires_at=expires_at
                    )

                    send_otp_email(existing_user.email, code)
            except EmailDeliveryError as exc:
                return Response(
                    {'error': str(exc)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            return Response(
                {
                    'message': 'NGO account already exists but is awaiting OTP verification. A new OTP has been sent to your email.',
                    'user': UserSerializer(existing_user).data,
                    'otp_resent': True,
                },
                status=status.HTTP_200_OK,
            )

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    'message': _flatten_serializer_errors(serializer.errors),
                    'errors': serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            self.perform_create(serializer)
        except EmailDeliveryError as exc:
            return Response(
                {
                    'message': str(exc),
                    'errors': {'email': [str(exc)]},
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except serializers.ValidationError as exc:
            detail = exc.detail if hasattr(exc, 'detail') else {'detail': [str(exc)]}
            return Response(
                {
                    'message': _flatten_serializer_errors(detail),
                    'errors': detail,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except IntegrityError as exc:
            return Response(
                {
                    'message': _friendly_integrity_error_message(exc),
                    'errors': {'detail': [_friendly_integrity_error_message(exc)]},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        headers = self.get_success_headers(serializer.data)
        return Response(
            {
                'message': 'NGO registered successfully. OTP sent to email. Awaiting admin verification.',
                'user': serializer.data,
            },
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    'message': _flatten_serializer_errors(serializer.errors),
                    'errors': serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)

        return Response({
            'message': 'Login successful.',
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data,
        }, status=status.HTTP_200_OK)


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = (request.data.get('email') or '').strip()
        otp_code = str(request.data.get('otp') or '').strip()

        if not email or not otp_code:
            return Response(
                {'error': 'Email and OTP are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.filter(email__iexact=email).order_by('-id').first()
        if not user:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get the latest OTP for this user
        otp_obj = OTPCode.objects.filter(user=user).order_by('-created_at').first()

        if not otp_obj:
            return Response(
                {'error': 'No OTP found for this user'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not otp_obj.is_valid():
            if otp_obj.is_used:
                return Response(
                    {'error': 'OTP already used'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                return Response(
                    {'error': 'OTP expired'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if otp_obj.code != otp_code:
            return Response(
                {'error': 'Invalid OTP'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Mark OTP as used
        otp_obj.is_used = True
        otp_obj.save()

        # Mark email as verified
        user.is_email_verified = True
        user.save()

        if not user.is_active:
            return Response({
                'message': 'OTP verified successfully. Your account is pending admin approval.',
                'requires_admin_approval': True,
                'user': UserSerializer(user).data,
            }, status=status.HTTP_200_OK)

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'OTP verified successfully',
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data,
        }, status=status.HTTP_200_OK)


class RequestOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response(
                {'error': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.filter(email__iexact=email).order_by('-id').first()
        if not user:
            # Don't reveal if user exists or not for security
            return Response(
                {'message': 'If user exists, OTP will be sent to their email'},
                status=status.HTTP_200_OK
            )

        # Generate new OTP
        import random
        from datetime import timedelta
        
        try:
            with transaction.atomic():
                code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
                expires_at = timezone.now() + timedelta(minutes=10)
                
                OTPCode.objects.create(
                    user=user,
                    code=code,
                    expires_at=expires_at
                )

                send_otp_email(user.email, code)
        except EmailDeliveryError as exc:
            return Response(
                {'error': str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            {'message': 'OTP sent to email'},
            status=status.HTTP_200_OK
        )


class CurrentUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
    
