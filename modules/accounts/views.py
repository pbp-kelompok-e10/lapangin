from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import json
from .forms import CustomUserCreationForm
import datetime
from modules.booking.models import Booking
from modules.user.models import UserProfile
from datetime import date
from django.views.decorators.http import require_POST
from modules.user.forms import UserProfileForm

def register(request):
    form = CustomUserCreationForm()

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({
                'status': 'success',
                'message': 'Account created! You will be redirected to login.'
            }, status=201)
        else:
            errors = json.loads(form.errors.as_json())
            return JsonResponse({'status': 'error', 'errors': errors}, status=400)
    
    return render(request, 'register.html')
    

def login_user(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            response =  JsonResponse({
                'status': 'success',
                'message': 'Login succesfull!',
                'redirect_url': reverse('main:show_main')
            })
            response.set_cookie('last_login', str(datetime.datetime.now()))
            return response
        else:
            errors = json.loads(form.errors.as_json())
            return JsonResponse({'status': 'error', 'errors': errors}, status=400)

    return render(request, 'login.html')

@csrf_exempt
def logout_user(request):
    logout(request)

    redirect_url = reverse('accounts:login');

    response = JsonResponse({
        'status': 'success',
        'message': 'You have been logged out.',
        'redirect_url': redirect_url
    })

    response.delete_cookie('last_login');

    return response

def get_page_data(request):
    if request.user.is_authenticated:
        # Get or create UserProfile
        profile, created = UserProfile.objects.get_or_create(
            user=request.user,
            defaults={'full_name': f"{request.user.first_name} {request.user.last_name}".strip()}
        )
        return JsonResponse({
            'is_authenticated': True,
            'user_id': request.user.id,
            'username': request.user.username,
            'full_name': profile.full_name or request.user.get_full_name() or request.user.username,
            'phone': profile.phone,
            'address': profile.address,
            'is_staff': request.user.is_staff,
            'is_superuser': request.user.is_superuser,
        })
    else:
        return JsonResponse({'is_authenticated': False})

@login_required(login_url='/accounts/login/')
def profile_page(request):
    # Get or create UserProfile
    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={'full_name': f"{request.user.first_name} {request.user.last_name}".strip()}
    )
    
    user_bookings = Booking.objects.filter(user=request.user).select_related('venue').order_by('-booking_date')
    bookings_data = []
    for booking in user_bookings:
        can_modify = booking.booking_date >= date.today()
        bookings_data.append({
            'booking_id': booking.id,
            'venue_id': booking.venue.id,
            'venue_name': booking.venue.name,
            'venue_thumbnail': booking.venue.thumbnail if booking.venue.thumbnail else '/static/img/default-thumbnail.jpg',
            'booking_date': booking.booking_date.isoformat(),
            'created_at': booking.created_at.isoformat(),
            'can_modify': can_modify,
            'url_detail': reverse('venue:venue_detail', args=[booking.venue.id]),
        })

    context = {
        'user': request.user,
        'profile': profile,
        'bookings': bookings_data
    }
    return render(request, 'profile.html', context)

@csrf_exempt
@require_POST
@login_required
def edit_profile(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    form = UserProfileForm(request.POST, instance=profile)
    full_name = request.POST.get('full_name', '').strip()
    if full_name:
        profile.full_name = full_name
    if form.is_valid():
        form.save()
        return JsonResponse({'status': 'success', 'message': 'Profil berhasil diupdate.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Data tidak valid.'})