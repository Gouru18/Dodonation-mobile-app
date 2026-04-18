from rest_framework import serializers
from .models import DonorProfile, NGOProfile, NGOPermitApplication
from accounts.serializers import UserSerializer

class DonorProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = DonorProfile
        fields = ['id', 'user', 'full_name', 'address']


class NGOPermitApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = NGOPermitApplication
        fields = ['id', 'ngo', 'permit_file', 'submitted_at', 'status', 'reviewed_at', 'rejection_reason']
        read_only_fields = ['id', 'submitted_at', 'reviewed_at']


class NGOProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    permit_application = NGOPermitApplicationSerializer(read_only=True)

    class Meta:
        model = NGOProfile
        fields = ['id', 'user', 'organization_name', 'registration_number', 'address', 'permit_application']


class NGOPermitUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = NGOPermitApplication
        fields = ['permit_file']

    def create(self, validated_data):
        user = self.context['request'].user
        try:
            ngo_profile = user.ngo_profile
        except:
            raise serializers.ValidationError("User does not have an NGO profile")
        
        # Delete old pending/rejected permits
        NGOPermitApplication.objects.filter(ngo=ngo_profile).exclude(status='approved').delete()
        
        permit = NGOPermitApplication.objects.create(
            ngo=ngo_profile,
            **validated_data
        )
        return permit


class NGOPermitApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = NGOPermitApplication
        fields = ['status', 'rejection_reason']