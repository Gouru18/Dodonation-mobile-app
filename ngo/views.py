from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from users.decorators import login_ngo, login_donor
from .forms import NGOSignupForm, NGOProfileForm
from core.models import ClaimRequest
from .models import NGOProfile
from .forms import UserEditForm

# ---------------- HTML Views (keep as-is) ----------------

def ngo_signup_view(request):
    if request.method == 'POST':
        form = NGOSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = "ngo"
            user.set_password(form.cleaned_data['password'])
            user.is_active = False  # wait for admin approval
            user.save()

            NGOProfile.objects.create(
                user=user,
                name=form.cleaned_data['name'],
                reg_number=form.cleaned_data['reg_number']
            )
            
            messages.info(request, "NGO verification is pending.")
            return redirect('ngo_pending')
    else:
        form = NGOSignupForm()
    return render(request, 'ngo/ngo_signup.html', {'form': form})

def ngo_pending_view(request):
    return render(request, 'ngo/ngo_pending.html')


@login_ngo
def ngo_account_view(request):
    ngo_profile = request.user.ngo_profile
    claimed = ClaimRequest.objects.filter(receiver=ngo_profile, status='accepted')
    requests = ClaimRequest.objects.filter(receiver=ngo_profile)

    stats = {
        'total_requests': requests.count(),
        'total_claimed': claimed.count(),
        'success_rate': round((claimed.count() / requests.count()) * 100, 2) if requests else 0,
    }
    return render(request, 'ngo/ngo_account.html', {
        'receiver': ngo_profile,
        'requests': requests,
        'claimed': claimed,
        'stats': stats,
    })


def ngo_public_profile(request, ngo_Id):
    ngo = get_object_or_404(NGOProfile, pk=ngo_Id)
    requests_made = ClaimRequest.objects.filter(receiver=ngo).select_related("donation")
    
    context = {
        'ngo': ngo,
        'requests_made': requests_made,
    }
    return render(request, 'ngo/ngo_public_profile.html', context)


@login_ngo
def ngo_edit_view(request):
    if not hasattr(request.user, 'ngo_profile'):
        messages.error(request, "You must be an NGO to edit this page.")
        return redirect('ngo_account')

    ngo_profile = request.user.ngo_profile

    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=request.user)
        profile_form = NGOProfileForm(request.POST, instance=ngo_profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "NGO profile updated successfully.")
            return redirect('ngo_account')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = NGOProfileForm(instance=ngo_profile)

    return render(request, 'ngo/ngo_edit.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })

# ---------------- API Views (for mobile app) ----------------
from rest_framework import status, response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from api.serializers import NGOProfileSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_permit(request):
    """
    Endpoint for NGO to upload permit file
    """
    ngo_profile = request.user.ngo_profile
    file = request.FILES.get('permit_file')
    if file:
        ngo_profile.permit_file = file
        ngo_profile.verification_status = 'pending'
        ngo_profile.save()
        serializer = NGOProfileSerializer(ngo_profile)
        return response.Response(serializer.data, status=status.HTTP_200_OK)
    return response.Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_verification_status(request):
    """
    Endpoint for NGO to check verification status
    """
    ngo_profile = request.user.ngo_profile
    serializer = NGOProfileSerializer(ngo_profile)
    return response.Response(serializer.data)