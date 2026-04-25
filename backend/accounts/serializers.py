from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
import random
from profiles.models import DonorProfile, NGOProfile, NGOPermitApplication
from accounts.models import OTPCode
from core.email_utils import send_otp_email

User = get_user_model()

class RegisterDonorSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)
    full_name = serializers.CharField(max_length=255, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'full_name', 'phone']

    def validate_email(self, value):
        existing_user = User.objects.filter(email__iexact=value).order_by('-id').first()
        if existing_user:
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_username(self, value):
        existing_user = User.objects.filter(username__iexact=value).order_by('-id').first()
        if existing_user:
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def create(self, validated_data):
        full_name = validated_data.pop('full_name')

        with transaction.atomic():
            user = User.objects.create_user(
                username=validated_data['username'],
                email=validated_data['email'],
                password=validated_data['password'],
                role='donor',
                phone=validated_data.get('phone', ''),
                is_active=True
            )

            DonorProfile.objects.create(user=user, full_name=full_name)

            # Keep OTP generation logic unchanged while ensuring failures roll back registration.
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

        send_otp_email(user.email, code)


class RegisterNGOSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)
    organization_name = serializers.CharField(max_length=255, write_only=True)
    registration_number = serializers.CharField(required=False, allow_blank=True, write_only=True)
    permit_file = serializers.FileField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'organization_name', 'registration_number', 'phone', 'permit_file']

    def validate_email(self, value):
        existing_user = User.objects.filter(email__iexact=value).order_by('-id').first()
        if existing_user:
            if existing_user.role == 'ngo' and not existing_user.is_active:
                raise serializers.ValidationError("This NGO account is pending admin approval. Please wait until it is activated.")
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_username(self, value):
        existing_user = User.objects.filter(username__iexact=value).order_by('-id').first()
        if existing_user:
            if existing_user.role == 'ngo' and not existing_user.is_active:
                raise serializers.ValidationError("This NGO account is pending admin approval. Please wait until it is activated.")
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def create(self, validated_data):
        organization_name = validated_data.pop('organization_name')
        registration_number = validated_data.pop('registration_number', '')
        permit_file = validated_data.pop('permit_file')

        with transaction.atomic():
            user = User.objects.create_user(
                username=validated_data['username'],
                email=validated_data['email'],
                password=validated_data['password'],
                role='ngo',
                phone=validated_data.get('phone', ''),
                is_active=False  # NGO must be verified by admin
            )

            ngo_profile = NGOProfile.objects.create(
                user=user,
                organization_name=organization_name,
                registration_number=registration_number
            )

            NGOPermitApplication.objects.create(
                ngo=ngo_profile,
                permit_file=permit_file,
                status='pending',
            )

            # Keep OTP generation logic unchanged while ensuring failures roll back registration.
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

        send_otp_email(user.email, code)


class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        identifier = data.get('identifier', '').strip()
        password = data.get('password')

        user = User.objects.filter(
            Q(username__iexact=identifier) | Q(email__iexact=identifier)
        ).order_by('-id').first()

        if not user:
            raise serializers.ValidationError("User not found.")
        if not user.check_password(password):
            raise serializers.ValidationError("Incorrect password.")
        if not user.is_active:
            raise serializers.ValidationError("User is not active. Please wait for admin verification.")
        
        data['user'] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'role', 'phone', 'is_active', 'is_staff', 'is_superuser']
        read_only_fields = ['id', 'role', 'is_staff', 'is_superuser']

    def get_role(self, obj):
        return obj.role or ('admin' if obj.is_staff or obj.is_superuser else '')
