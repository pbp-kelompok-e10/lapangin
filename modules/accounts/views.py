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
        return JsonResponse({
            'is_authenticated': True,
            'user_id': request.user.id,
            'username': request.user.username,
            'name': 'Prasetya Surya Syahputra',
            'npm': '2406398381',
            'class': 'PBP E',
            'is_staff': request.user.is_staff,
            'is_superuser': request.user.is_superuser,
        })
    else:
        return JsonResponse({'is_authenticated': False})