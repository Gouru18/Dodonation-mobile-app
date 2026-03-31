import json
from datetime import date

from django.db import transaction
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from core.models import ClaimRequest, Donation


def _serialize_donation(donation: Donation) -> dict:
    return {
        'id': donation.id,
        'title': donation.title,
        'description': donation.description,
        'category': donation.category,
        'quantity': donation.quantity,
        'expiry_date': donation.expiry_date.isoformat(),
        'location': donation.location,
        'status': donation.status,
        'date_created': donation.date_created.isoformat(),
        'donor': {
            'id': donation.donor.donorID,
            'username': donation.donor.user.username,
        },
    }


def _serialize_request(claim_request: ClaimRequest) -> dict:
    return {
        'id': claim_request.id,
        'donation': {
            'id': claim_request.donation.id,
            'title': claim_request.donation.title,
            'status': claim_request.donation.status,
        },
        'receiver': {
            'id': claim_request.receiver.receiverID,
            'name': claim_request.receiver.name,
            'username': claim_request.receiver.user.username,
        },
        'status': claim_request.status,
        'date_requested': claim_request.date_requested.isoformat(),
    }


def _parse_json_body(request):
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        raise ValueError('Invalid JSON body.')


@csrf_exempt
@require_http_methods(['POST'])
def api_login(request):
    try:
        payload = _parse_json_body(request)
    except ValueError as exc:
        return JsonResponse({'error': str(exc)}, status=400)

    username = payload.get('username')
    password = payload.get('password')
    if not username or not password:
        return JsonResponse({'error': 'username and password are required.'}, status=400)

    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse({'error': 'Invalid username or password.'}, status=401)

    if getattr(user, 'role', None) == 'ngo' and not user.is_active:
        return JsonResponse({'error': 'NGO verification is still pending.'}, status=403)

    login(request, user)
    return JsonResponse({
        'user': {
            'username': user.username,
            'email': user.email,
            'role': getattr(user, 'role', None),
        }
    })


@csrf_exempt
@require_http_methods(['POST'])
def api_logout(request):
    logout(request)
    return JsonResponse({'success': True})


@csrf_exempt
@require_http_methods(['GET', 'POST'])
def api_donations(request):
    if request.method == 'GET':
        donations = Donation.objects.all().order_by('-date_created')
        return JsonResponse({'donations': [_serialize_donation(d) for d in donations]})

    if request.method == 'POST':
        if not request.user.is_authenticated or request.user.role != 'donor':
            return JsonResponse({'error': 'Authentication required as donor.'}, status=401)

        donor_profile = getattr(request.user, 'donor_profile', None)
        if donor_profile is None:
            return JsonResponse({'error': 'Donor profile does not exist.'}, status=400)

        try:
            payload = _parse_json_body(request)
        except ValueError as exc:
            return JsonResponse({'error': str(exc)}, status=400)

        required = ['title', 'description', 'category', 'quantity', 'expiry_date', 'location']
        missing = [field for field in required if not payload.get(field)]
        if missing:
            return JsonResponse({'error': f'Missing fields: {", ".join(missing)}'}, status=400)

        try:
            expiry = date.fromisoformat(payload['expiry_date'])
        except ValueError:
            return JsonResponse({'error': 'expiry_date must be in YYYY-MM-DD format.'}, status=400)

        try:
            quantity = int(payload['quantity'])
            if quantity < 1:
                raise ValueError
        except (ValueError, TypeError):
            return JsonResponse({'error': 'quantity must be a positive integer.'}, status=400)

        donation = Donation.objects.create(
            title=payload['title'],
            description=payload['description'],
            category=payload['category'],
            quantity=quantity,
            expiry_date=expiry,
            location=payload['location'],
            donor=donor_profile,
        )

        return JsonResponse({'donation': _serialize_donation(donation)}, status=201)

    return HttpResponseNotAllowed(['GET', 'POST'])


@csrf_exempt
@require_http_methods(['GET', 'POST'])
def api_requests(request):
    if request.method == 'GET':
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required.'}, status=401)

        if request.user.role == 'ngo':
            receiver = getattr(request.user, 'ngo_profile', None)
            if receiver is None:
                return JsonResponse({'error': 'NGO profile does not exist.'}, status=400)
            requests_qs = ClaimRequest.objects.filter(receiver=receiver).order_by('-date_requested')
        elif request.user.role == 'donor':
            donor_profile = getattr(request.user, 'donor_profile', None)
            if donor_profile is None:
                return JsonResponse({'error': 'Donor profile does not exist.'}, status=400)
            requests_qs = ClaimRequest.objects.filter(donation__donor=donor_profile).order_by('-date_requested')
        else:
            return JsonResponse({'error': 'Only donor and NGO users can list requests.'}, status=403)

        return JsonResponse({'requests': [_serialize_request(req) for req in requests_qs]})

    if request.method == 'POST':
        if not request.user.is_authenticated or request.user.role != 'ngo':
            return JsonResponse({'error': 'Authentication required as NGO.'}, status=401)

        receiver = getattr(request.user, 'ngo_profile', None)
        if receiver is None:
            return JsonResponse({'error': 'NGO profile does not exist.'}, status=400)

        try:
            payload = _parse_json_body(request)
        except ValueError as exc:
            return JsonResponse({'error': str(exc)}, status=400)

        donation_id = payload.get('donation_id')
        if not donation_id:
            return JsonResponse({'error': 'donation_id is required.'}, status=400)

        donation = get_object_or_404(Donation, id=donation_id)
        if ClaimRequest.objects.filter(donation=donation, receiver=receiver).exists():
            return JsonResponse({'error': 'Request already exists for this donation.'}, status=400)

        claim_request = ClaimRequest.objects.create(donation=donation, receiver=receiver, status='pending')
        return JsonResponse({'request': _serialize_request(claim_request)}, status=201)

    return HttpResponseNotAllowed(['GET', 'POST'])


@csrf_exempt
@require_http_methods(['POST'])
def api_request_action(request, request_id):
    if not request.user.is_authenticated or request.user.role != 'donor':
        return JsonResponse({'error': 'Authentication required as donor.'}, status=401)

    donor_profile = getattr(request.user, 'donor_profile', None)
    if donor_profile is None:
        return JsonResponse({'error': 'Donor profile does not exist.'}, status=400)

    claim_request = get_object_or_404(ClaimRequest, id=request_id, donation__donor=donor_profile)

    try:
        payload = _parse_json_body(request)
    except ValueError as exc:
        return JsonResponse({'error': str(exc)}, status=400)

    action = payload.get('action')
    if action not in ('accept', 'reject'):
        return JsonResponse({'error': 'Action must be accept or reject.'}, status=400)

    if claim_request.status != 'pending':
        return JsonResponse({'error': 'Only pending requests can be acted on.'}, status=400)

    if action == 'accept':
        with transaction.atomic():
            claim_request.status = 'accepted'
            claim_request.donation.status = 'claimed'
            claim_request.donation.save()
            claim_request.save()
            ClaimRequest.objects.filter(donation=claim_request.donation, status='pending').exclude(id=claim_request.id).update(status='rejected')
    else:
        claim_request.status = 'rejected'
        claim_request.save()

    return JsonResponse({'request': _serialize_request(claim_request)})
