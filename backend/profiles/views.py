from rest_framework import generics, permissions
from .models import DonorProfile, NGOProfile
from .serializers import DonorProfileSerializer, NGOProfileSerializer

class DonorProfileDetailView(generics.RetrieveUpdateAPIView):
    queryset = DonorProfile.objects.all()
    serializer_class = DonorProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

class NGOProfileDetailView(generics.RetrieveUpdateAPIView):
    queryset = NGOProfile.objects.all()
    serializer_class = NGOProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
