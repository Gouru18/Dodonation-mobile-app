from rest_framework import serializers
from core.models import Donation
from core.models import ClaimRequest
from core.models import GeneralReview
from core.models import Report
from users.models import User
from ngo.models import NGOProfile
from donor.models import DonorProfile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']

class DonationSerializer(serializers.ModelSerializer):
    donor_username = serializers.CharField(source='donor.user.username', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        elif obj.image:
            return obj.image.url
        return None

    class Meta:
        model = Donation
        fields = [
            'id', 'title', 'description', 'quantity', 'location', 
            'expiry_date', 'category', 'category_display', 
            'status', 'status_display', 'date_created', 
            'donor', 'donor_username', 'image'
        ]

class ClaimRequestSerializer(serializers.ModelSerializer):
    donation_title = serializers.CharField(source='donation.title', read_only=True)
    receiver_name = serializers.CharField(source='receiver.user.username', read_only=True)

    class Meta:
        model = ClaimRequest
        fields = ['id', 'donation', 'donation_title', 'receiver', 'receiver_name', 'status', 'date_requested']

class GeneralReviewSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = GeneralReview
        fields = ['id', 'user_username', 'name', 'email', 'message', 'created_at']

class ReportSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Report
        fields = ['id', 'user_username', 'name', 'email', 'message', 'created_at']

class NGOProfileSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_phone_no = serializers.CharField(source='user.phone_no', read_only=True)

    class Meta:
        model = NGOProfile
        fields = ['receiverID', 'user_username', 'user_email', 'user_phone_no', 'name', 'reg_number']

class DonorProfileSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_phone_no = serializers.CharField(source='user.phone_no', read_only=True)

    class Meta:
        model = DonorProfile
        fields = ['donorID','user_username', 'user_email', 'user_phone_no']

    def update(self, instance, validated_data):
        # Extract and update user fields
        if 'user' in validated_data:
            user_data = validated_data.pop('user')
            user = instance.user
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()
        
        # Update DonorProfile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance


class NGOSignupSerializer(serializers.Serializer):
    """Serializer for NGO signup - creates both User and NGOProfile"""
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    phone_no = serializers.CharField(max_length=8)
    name = serializers.CharField(max_length=100)
    reg_number = serializers.CharField(max_length=50)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def validate_name(self, value):
        if NGOProfile.objects.filter(name=value).exists():
            raise serializers.ValidationError("NGO name already exists.")
        return value

    def validate_reg_number(self, value):
        if NGOProfile.objects.filter(reg_number=value).exists():
            raise serializers.ValidationError("Registration number already exists.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            phone_no=validated_data['phone_no'],
            role='ngo'
        )
        
        ngo_profile = NGOProfile.objects.create(
            user=user,
            name=validated_data['name'],
            reg_number=validated_data['reg_number']
        )
        
        return ngo_profile


class DonorSignupSerializer(serializers.Serializer):
    """Serializer for Donor signup - creates both User and DonorProfile"""
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    phone_no = serializers.CharField(max_length=8)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            phone_no=validated_data['phone_no'],
            role='donor'
        )
        
        donor_profile = DonorProfile.objects.create(user=user)
        
        return donor_profile


