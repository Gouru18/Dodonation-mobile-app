from rest_framework import serializers
from django.contrib.auth import get_user_model
from profiles.models import DonorProfile, NGOProfile

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    full_name = serializers.CharField(required=False)
    organization_name = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ['username','email', 'password', 'role', 'phone', 'full_name', 'organization_name']

    def create(self, validated_data):
        full_name = validated_data.pop('full_name', '')
        organization_name = validated_data.pop('organization_name', '')

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get['email'],
            password=validated_data['password'],
            role=validated_data['role'],
            phone=validated_data.get['phone']
        )

        if user.role == 'donor':
            DonorProfile.objects.create(user=user, full_name=full_name)
        elif user.role == 'ngo':
            NGOProfile.objects.create(user=user, organization_name=organization_name)

        return user