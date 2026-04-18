from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random
from profiles.models import DonorProfile, NGOProfile
from accounts.models import OTPCode

User = get_user_model()

class RegisterDonorSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    full_name = serializers.CharField(max_length=255)

    class Meta:
        model = User
        fields = ['email', 'password', 'full_name', 'phone']

    def create(self, validated_data):
        full_name = validated_data.pop('full_name')
        
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            role='donor',
            phone=validated_data.get('phone', ''),
            is_active=True
        )

        DonorProfile.objects.create(user=user, full_name=full_name)
        
        # Send OTP
        self.send_otp(user)
        
        return user

    @staticmethod
    def send_otp(user):
        """Generate and send OTP to user"""
        code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        expires_at = timezone.now() + timedelta(minutes=10)
        
        OTPCode.objects.create(
            user=user,
            code=code,
            expires_at=expires_at
        )
        
        # TODO: Send OTP via email
        # send_otp_email(user.email, code)
        print(f"OTP for {user.email}: {code}")  # For debugging


class RegisterNGOSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    organization_name = serializers.CharField(max_length=255)
    registration_number = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'organization_name', 'registration_number', 'phone']

    def create(self, validated_data):
        organization_name = validated_data.pop('organization_name')
        registration_number = validated_data.pop('registration_number', '')
        
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            role='ngo',
            phone=validated_data.get('phone', ''),
            is_active=False  # NGO must be verified by admin
        )

        NGOProfile.objects.create(
            user=user,
            organization_name=organization_name,
            registration_number=registration_number
        )
        
        # Send OTP
        self.send_otp(user)
        
        return user

    @staticmethod
    def send_otp(user):
        """Generate and send OTP to user"""
        code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        expires_at = timezone.now() + timedelta(minutes=10)
        
        OTPCode.objects.create(
            user=user,
            code=code,
            expires_at=expires_at
        )
        
        # TODO: Send OTP via email
        # send_otp_email(user.email, code)
        print(f"OTP for {user.email}: {code}")  # For debugging


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        try:
            user = User.objects.get(email=email)
            if not user.check_password(password):
                raise serializers.ValidationError("Invalid credentials")
            if not user.is_active:
                raise serializers.ValidationError("User is not active. Please wait for admin verification.")
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials")
        
        data['user'] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'role', 'phone', 'is_active']
        read_only_fields = ['id', 'role']