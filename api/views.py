from rest_framework import response
from rest_framework.decorators import api_view
from django.shortcuts import render, get_object_or_404

from core.models import Donation
from core.models import ClaimRequest
from core.models import GeneralReview
from core.models import Report

from .serializers import DonationSerializer
from .serializers import ClaimRequestSerializer
from .serializers import GeneralReviewSerializer
from .serializers import ReportSerializer

from users.models import User
from ngo.models import NGOProfile
from donor.models import DonorProfile

from .serializers import UserSerializer
from .serializers import NGOProfileSerializer
from .serializers import DonorProfileSerializer

from users.decorators import login_ngo, login_donor, login_required_home

@api_view(['GET'])
def test(request, format=None):
    return response.Response({
        'message': 'Test endpoint is working!',
    })

@api_view(['POST'])
def login(request, format=None):
    username = request.data.get('username')
    password = request.data.get('password')
    user = User.objects.filter(username=username).first()
    if user and user.check_password(password):
        serializer = UserSerializer(user)
        return response.Response(serializer.data)
    return response.Response({'error': 'Invalid credentials'}, status=400)

@api_view(['POST'])
def selct_role(request, format=None):
    role = request.data.get('role')
    if role in ['donor', 'ngo']:
        return response.Response({'message': f'Role {role} selected'})
    return response.Response({'error': 'Invalid role'}, status=400)

@api_view(['POST'])
def create_ngo_profile(request, format=None):
    serializer = NGOProfileSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return response.Response(serializer.data, status=201)
    return response.Response(serializer.errors, status=400)

@api_view(['POST'])
def create_donor_profile(request, format=None):
    serializer = DonorProfileSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return response.Response(serializer.data, status=201)
    return response.Response(serializer.errors, status=400)

@login_ngo
@api_view(['GET'])
def get_ngo_profiles(request, format=None):
    ngos = NGOProfile.objects.all()
    serializer = NGOProfileSerializer(ngos, many=True)
    return response.Response(serializer.data)

@login_donor
@api_view(['GET'])
def get_donor_profiles(request, format=None):
    donors = DonorProfile.objects.all()
    serializer = DonorProfileSerializer(donors, many=True)
    return response.Response(serializer.data)

@api_view(['GET'])
def get_donations(request, format=None):
    donations = Donation.objects.all()
    serializer = DonationSerializer(donations, many=True)
    return response.Response(serializer.data)

@login_donor
@api_view(['GET'])
def get_claim_requests(request, format=None):
    claim_requests = ClaimRequest.objects.all()
    serializer = ClaimRequestSerializer(claim_requests, many=True)
    return response.Response(serializer.data)

@api_view(['GET'])
def get_general_reviews(request, format=None):
    reviews = GeneralReview.objects.all()
    serializer = GeneralReviewSerializer(reviews, many=True)
    return response.Response(serializer.data)

@api_view(['GET'])
def get_reports(request, format=None):
    reports = Report.objects.all()
    serializer = ReportSerializer(reports, many=True)
    return response.Response(serializer.data)

@login_donor
@api_view(['POST'])
def create_donation(request, format=None):
    serializer = DonationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return response.Response(serializer.data, status=201)
    return response.Response(serializer.errors, status=400)

@login_ngo
@api_view(['POST'])
def create_claim_request(request, format=None):
    serializer = ClaimRequestSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return response.Response(serializer.data, status=201)
    return response.Response(serializer.errors, status=400)

@login_required_home
@api_view(['POST'])
def create_general_review(request, format=None):
    serializer = GeneralReviewSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return response.Response(serializer.data, status=201)
    return response.Response(serializer.errors, status=400)

@login_required_home
@api_view(['POST'])
def create_report(request, format=None):
    serializer = ReportSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return response.Response(serializer.data, status=201)
    return response.Response(serializer.errors, status=400)


@api_view(['GET', 'PATCH', 'DELETE'])
@login_donor
def donation_detail(request, pk):
    donation = get_object_or_404(Donation, pk=pk)
    
    if request.method == 'PATCH':
        serializer = DonationSerializer(donation, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return response.Response(serializer.data)
        return response.Response(serializer.errors, status=400)
    
    # ... handle GET or DELETE if needed






