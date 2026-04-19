from rest_framework import serializers

from accounts.models import User, OTPCode
from donations.models import Donation, ClaimRequest
from meetings.models import Meeting
from profiles.models import DonorProfile, NGOProfile, NGOPermitApplication


class AdminUserSummarySerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'is_active', 'is_staff', 'is_superuser']

    def get_role(self, obj):
        return obj.role or ('admin' if obj.is_staff or obj.is_superuser else '')


class AdminNGOPermitSummarySerializer(serializers.ModelSerializer):
    permit_file_url = serializers.SerializerMethodField()

    class Meta:
        model = NGOPermitApplication
        fields = ['id', 'status', 'submitted_at', 'reviewed_at', 'rejection_reason', 'permit_file_url']

    def get_permit_file_url(self, obj):
        request = self.context.get('request')
        if obj.permit_file and getattr(obj.permit_file, 'url', None):
            return request.build_absolute_uri(obj.permit_file.url) if request else obj.permit_file.url
        return None


class AdminUserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    ngo_organization_name = serializers.SerializerMethodField()
    ngo_registration_number = serializers.SerializerMethodField()
    ngo_permit = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'password',
            'role',
            'phone',
            'is_active',
            'is_staff',
            'is_superuser',
            'is_email_verified',
            'is_phone_verified',
            'ngo_organization_name',
            'ngo_registration_number',
            'ngo_permit',
        ]
        read_only_fields = ['id', 'ngo_organization_name', 'ngo_registration_number', 'ngo_permit']

    def validate_role(self, value):
        if value == '' and self.initial_data.get('is_staff'):
            return 'admin'
        return value

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        role = validated_data.get('role') or ('admin' if validated_data.get('is_staff') or validated_data.get('is_superuser') else 'donor')
        validated_data['role'] = role
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if (instance.is_staff or instance.is_superuser) and not instance.role:
            instance.role = 'admin'
        if password:
            instance.set_password(password)
        instance.save()
        return instance

    def get_ngo_organization_name(self, obj):
        ngo_profile = getattr(obj, 'ngo_profile', None)
        return getattr(ngo_profile, 'organization_name', None)

    def get_ngo_registration_number(self, obj):
        ngo_profile = getattr(obj, 'ngo_profile', None)
        return getattr(ngo_profile, 'registration_number', None)

    def get_ngo_permit(self, obj):
        ngo_profile = getattr(obj, 'ngo_profile', None)
        permit = getattr(ngo_profile, 'permit_application', None) if ngo_profile else None
        if not permit:
            return None
        return AdminNGOPermitSummarySerializer(permit, context=self.context).data


class AdminOTPCodeSerializer(serializers.ModelSerializer):
    user = AdminUserSummarySerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='user', write_only=True)

    class Meta:
        model = OTPCode
        fields = ['id', 'user', 'user_id', 'code', 'created_at', 'is_used', 'expires_at']
        read_only_fields = ['id', 'created_at']


class AdminDonorProfileSerializer(serializers.ModelSerializer):
    user = AdminUserSummarySerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role='donor'), source='user', write_only=True)

    class Meta:
        model = DonorProfile
        fields = ['id', 'user', 'user_id', 'full_name', 'address']
        read_only_fields = ['id']


class AdminNGOProfileSerializer(serializers.ModelSerializer):
    user = AdminUserSummarySerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role='ngo'), source='user', write_only=True)
    permit_application = AdminNGOPermitSummarySerializer(read_only=True)

    class Meta:
        model = NGOProfile
        fields = ['id', 'user', 'user_id', 'organization_name', 'registration_number', 'address', 'permit_application']
        read_only_fields = ['id', 'permit_application']


class AdminNGOPermitSerializer(serializers.ModelSerializer):
    ngo = AdminNGOProfileSerializer(read_only=True)
    ngo_id = serializers.PrimaryKeyRelatedField(queryset=NGOProfile.objects.all(), source='ngo', write_only=True, required=False)
    reviewed_by = AdminUserSummarySerializer(read_only=True)
    permit_file_url = serializers.SerializerMethodField()

    class Meta:
        model = NGOPermitApplication
        fields = [
            'id',
            'ngo',
            'ngo_id',
            'permit_file',
            'permit_file_url',
            'submitted_at',
            'status',
            'reviewed_by',
            'reviewed_at',
            'rejection_reason',
        ]
        read_only_fields = ['id', 'submitted_at', 'reviewed_by', 'reviewed_at', 'permit_file_url']

    def get_permit_file_url(self, obj):
        request = self.context.get('request')
        if obj.permit_file and getattr(obj.permit_file, 'url', None):
            return request.build_absolute_uri(obj.permit_file.url) if request else obj.permit_file.url
        return None


class AdminDonationSerializer(serializers.ModelSerializer):
    donor = AdminUserSummarySerializer(read_only=True)
    donor_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role='donor'), source='donor', write_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Donation
        fields = [
            'id',
            'donor',
            'donor_id',
            'title',
            'description',
            'category',
            'quantity',
            'expiry_date',
            'latitude',
            'longitude',
            'status',
            'image',
            'image_url',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'image_url']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and getattr(obj.image, 'url', None):
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None


class AdminDonationSummarySerializer(serializers.ModelSerializer):
    donor = AdminUserSummarySerializer(read_only=True)

    class Meta:
        model = Donation
        fields = ['id', 'title', 'status', 'category', 'donor']


class AdminClaimRequestSerializer(serializers.ModelSerializer):
    donation = AdminDonationSummarySerializer(read_only=True)
    donation_id = serializers.PrimaryKeyRelatedField(queryset=Donation.objects.all(), source='donation', write_only=True)
    receiver = AdminUserSummarySerializer(read_only=True)
    receiver_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role='ngo'), source='receiver', write_only=True)

    class Meta:
        model = ClaimRequest
        fields = [
            'id',
            'donation',
            'donation_id',
            'receiver',
            'receiver_id',
            'status',
            'message',
            'date_requested',
            'date_responded',
        ]
        read_only_fields = ['id', 'date_requested', 'date_responded']


class AdminClaimRequestSummarySerializer(serializers.ModelSerializer):
    donation_title = serializers.CharField(source='donation.title', read_only=True)
    receiver_email = serializers.CharField(source='receiver.email', read_only=True)

    class Meta:
        model = ClaimRequest
        fields = ['id', 'donation_title', 'receiver_email', 'status']


class AdminMeetingSerializer(serializers.ModelSerializer):
    claim_request = AdminClaimRequestSummarySerializer(read_only=True)
    claim_request_id = serializers.PrimaryKeyRelatedField(queryset=ClaimRequest.objects.all(), source='claim_request', write_only=True)

    class Meta:
        model = Meeting
        fields = [
            'id',
            'claim_request',
            'claim_request_id',
            'scheduled_time',
            'meeting_link',
            'google_meet_space_name',
            'meeting_latitude',
            'meeting_longitude',
            'meeting_address',
            'status',
            'online_meeting_completed_at',
            'location_pinned_at',
            'physical_meeting_completed_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
