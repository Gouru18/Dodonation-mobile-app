from rest_framework import response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, get_object_or_404

from core.models import Donation
from core.models import ClaimRequest
from core.models import GeneralReview
from core.models import Report

from .serializers import DonationSerializer
from .serializers import ClaimRequestSerializer
from .serializers import GeneralReviewSerializer
from .serializers import ReportSerializer
from .permissions import IsNGO, IsNGOOwner, IsDonor, IsDonorOwner, IsLoggedIn, IsLoggedInOrReadOnly

from users.models import User
from ngo.models import NGOProfile
from donor.models import DonorProfile

from .serializers import UserSerializer
from .serializers import NGOProfileSerializer
from .serializers import DonorProfileSerializer

#from users.decorators import login_ngo, login_donor, login_required_home

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

@api_view(['GET'])
@permission_classes([IsNGO])
def get_ngo_profiles(request, format=None):
    ngos = NGOProfile.objects.all()
    serializer = NGOProfileSerializer(ngos, many=True)
    return response.Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsDonor])
def get_donor_profiles(request, format=None):
    donors = DonorProfile.objects.all()
    serializer = DonorProfileSerializer(donors, many=True)
    return response.Response(serializer.data)

@api_view(['GET'])
def get_donations(request, format=None):
    donations = Donation.objects.all()
    serializer = DonationSerializer(donations, many=True)
    return response.Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsNGO])
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

@api_view(['POST'])
@permission_classes([IsDonor])
def create_donation(request, format=None):
    serializer = DonationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return response.Response(serializer.data, status=201)
    return response.Response(serializer.errors, status=400)

@api_view(['POST'])
@permission_classes([IsNGO])
def create_claim_request(request, format=None):
    try:
        donation_id = request.data.get('donation')
        if not donation_id:
            return response.Response({'error': 'Donation ID is required'}, status=400)
        
        donation = get_object_or_404(Donation, pk=donation_id)
        ngo_profile = get_object_or_404(NGOProfile, user=request.user)
        
        # Check if a claim request already exists
        existing_request = ClaimRequest.objects.filter(
            donation=donation,
            receiver=ngo_profile
        ).first()
        
        if existing_request:
            return response.Response(
                {'error': 'You have already requested this donation'},
                status=400
            )
        
        claim_request = ClaimRequest.objects.create(
            donation=donation,
            receiver=ngo_profile
        )
        serializer = ClaimRequestSerializer(claim_request)
        return response.Response(serializer.data, status=201)
    except Exception as e:
        return response.Response({'error': str(e)}, status=400)

@api_view(['POST'])
@permission_classes([IsLoggedIn])
def create_general_review(request, format=None):
    serializer = GeneralReviewSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return response.Response(serializer.data, status=201)
    return response.Response(serializer.errors, status=400)

@api_view(['POST'])
@permission_classes([IsLoggedIn])
def create_report(request, format=None):
    serializer = ReportSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return response.Response(serializer.data, status=201)
    return response.Response(serializer.errors, status=400)


@api_view(['GET', 'PATCH', 'DELETE'])
def donation_detail(request, pk):
    donation = get_object_or_404(Donation, pk=pk)
    
    # For GET requests, allow anyone to view
    if request.method == 'GET':
        serializer = DonationSerializer(donation)
        return response.Response(serializer.data)
    
    # For PATCH and DELETE, check if user is the donor owner
    if request.method in ['PATCH', 'DELETE']:
        if not request.user or not request.user.is_authenticated:
            return response.Response(
                {'error': 'Authentication required'}, 
                status=401
            )
        
        if request.user.role != 'donor':
            return response.Response(
                {'error': 'Only donors can modify donations'}, 
                status=403
            )
        
        try:
            donor_profile = DonorProfile.objects.get(user=request.user)
            if donation.donor != donor_profile:
                return response.Response(
                    {'error': 'You can only modify your own donations'}, 
                    status=403
                )
        except DonorProfile.DoesNotExist:
            return response.Response(
                {'error': 'Donor profile not found'}, 
                status=404
            )
        
        if request.method == 'PATCH':
            serializer = DonationSerializer(donation, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return response.Response(serializer.data)
            return response.Response(serializer.errors, status=400)
        
        elif request.method == 'DELETE':
            donation.delete()
            return response.Response({'message': 'Donation deleted successfully'}, status=204)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsNGO])
def ngo_profile_detail(request, pk):
    ngo_profile = get_object_or_404(NGOProfile, pk=pk)
    
    if request.method == 'GET':
        serializer = NGOProfileSerializer(ngo_profile)
        return response.Response(serializer.data)
    
    if request.method in ['PATCH', 'DELETE']:
        # Only allow the NGO user to modify their own profile
        if ngo_profile.user != request.user:
            return response.Response(
                {'error': 'You can only modify your own profile'}, 
                status=403
            )
        
        if request.method == 'PATCH':
            serializer = NGOProfileSerializer(ngo_profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return response.Response(serializer.data)
            return response.Response(serializer.errors, status=400)
        
        elif request.method == 'DELETE':
            ngo_profile.delete()
            return response.Response({'message': 'NGO profile deleted successfully'}, status=204)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsDonor])
def donor_profile_detail(request, pk):
    donor_profile = get_object_or_404(DonorProfile, pk=pk)
    
    if request.method == 'GET':
        serializer = DonorProfileSerializer(donor_profile)
        return response.Response(serializer.data)
    
    if request.method in ['PATCH', 'DELETE']:
        # Only allow the Donor user to modify their own profile
        if donor_profile.user != request.user:
            return response.Response(
                {'error': 'You can only modify your own profile'}, 
                status=403
            )
        
        if request.method == 'PATCH':
            serializer = DonorProfileSerializer(donor_profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return response.Response(serializer.data)
            return response.Response(serializer.errors, status=400)
        
        elif request.method == 'DELETE':
            donor_profile.delete()
            return response.Response({'message': 'Donor profile deleted successfully'}, status=204)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsNGO])
def claim_request_detail(request, pk):
    claim_request = get_object_or_404(ClaimRequest, pk=pk)
    
    if request.method == 'GET':
        serializer = ClaimRequestSerializer(claim_request)
        return response.Response(serializer.data)
    
    if request.method in ['PATCH', 'DELETE']:
        # Only allow the NGO that created the claim request to modify it
        if claim_request.receiver.user != request.user:
            return response.Response(
                {'error': 'You can only modify your own claim requests'}, 
                status=403
            )
        
        if request.method == 'PATCH':
            serializer = ClaimRequestSerializer(claim_request, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return response.Response(serializer.data)
            return response.Response(serializer.errors, status=400)
        
        elif request.method == 'DELETE':
            claim_request.delete()
            return response.Response({'message': 'Claim request deleted successfully'}, status=204)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsLoggedIn])
def general_review_detail(request, pk):
    review = get_object_or_404(GeneralReview, pk=pk)
    
    if request.method == 'GET':
        serializer = GeneralReviewSerializer(review)
        return response.Response(serializer.data)
    
    if request.method in ['PATCH', 'DELETE']:
        # Only allow the user who created the review to modify it
        if review.reviewer != request.user:
            return response.Response(
                {'error': 'You can only modify your own reviews'}, 
                status=403
            )
        
        if request.method == 'PATCH':
            serializer = GeneralReviewSerializer(review, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return response.Response(serializer.data)
            return response.Response(serializer.errors, status=400)
        
        elif request.method == 'DELETE':
            review.delete()
            return response.Response({'message': 'Review deleted successfully'}, status=204)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsLoggedIn])
def report_detail(request, pk):
    report = get_object_or_404(Report, pk=pk)
    
    if request.method == 'GET':
        serializer = ReportSerializer(report)
        return response.Response(serializer.data)
    
    if request.method in ['PATCH', 'DELETE']:
        # Only allow the user who created the report to modify it
        if report.reporter != request.user:
            return response.Response(
                {'error': 'You can only modify your own reports'}, 
                status=403
            )
        
        if request.method == 'PATCH':
            serializer = ReportSerializer(report, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return response.Response(serializer.data)
            return response.Response(serializer.errors, status=400)
        
        elif request.method == 'DELETE':
            report.delete()
            return response.Response({'message': 'Report deleted successfully'}, status=204)




