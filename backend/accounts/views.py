from rest_framework import generics, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils import timezone

from .serializers import RegisterDonorSerializer, RegisterNGOSerializer, LoginSerializer, UserSerializer
from .models import OTPCode
from core.email_utils import send_otp_email

User = get_user_model()


class RegisterDonorView(generics.CreateAPIView):
    serializer_class = RegisterDonorSerializer
    permission_classes = [AllowAny]
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        if response.status_code == 201:
            response.data['message'] = 'Donor registered successfully. OTP sent to email.'
        return response


class RegisterNGOView(generics.CreateAPIView):
    serializer_class = RegisterNGOSerializer
    permission_classes = [AllowAny]
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        if response.status_code == 201:
            response.data['message'] = 'NGO registered successfully. OTP sent to email. Awaiting admin verification.'
        return response


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data,
        }, status=status.HTTP_200_OK)


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        otp_code = request.data.get('otp')

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
        
        code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        expires_at = timezone.now() + timedelta(minutes=10)
        
        OTPCode.objects.create(
            user=user,
            code=code,
            expires_at=expires_at
        )

        send_otp_email(user.email, code)

        return Response(
            {'message': 'OTP sent to email'},
            status=status.HTTP_200_OK
        )


class CurrentUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
    
