from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Q
from .models import UserProfile
from .forms import UserForm, UserProfileForm
import json


# Helper function to check if user is admin
def is_admin(user):
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(is_admin)
def user_list(request):
    """Display list of all users"""
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    users = User.objects.all().select_related('profile').order_by('-date_joined')
    
    # Search filter
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    # Status filter
    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)
    
    # Pagination
    paginator = Paginator(users, 10)  # Show 10 users per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'users': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'inactive_users': User.objects.filter(is_active=False).count(),
    }
    
    return render(request, 'user_list.html', context)

@login_required
@user_passes_test(is_admin)
def user_detail(request, user_id):
    """View details of a specific user"""
    user = get_object_or_404(User, id=user_id)
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    context = {
        'user_data': user,
        'profile': profile,
    }
    
    return render(request, 'user_detail.html', context)

@login_required
@user_passes_test(is_admin)
def user_create(request):
    """Create a new user"""
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        
        if user_form.is_valid() and profile_form.is_valid():
            # Create user
            user = user_form.save(commit=False)
            password = user_form.cleaned_data.get('password')
            if password:
                user.set_password(password)
            user.save()
            
            # Create profile
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'User created successfully!',
                'redirect_url': '/user/list/'
            })
        else:
            errors = {}
            if user_form.errors:
                errors.update(user_form.errors)
            if profile_form.errors:
                errors.update(profile_form.errors)
            
            return JsonResponse({
                'status': 'error',
                'errors': errors
            }, status=400)
    
    user_form = UserForm()
    profile_form = UserProfileForm()
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'mode': 'create'
    }
    
    return render(request, 'user_form.html', context)

@login_required
@user_passes_test(is_admin)
def user_edit(request, user_id):
    """Edit existing user"""
    user = get_object_or_404(User, id=user_id)
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            # Update user
            user = user_form.save(commit=False)
            password = user_form.cleaned_data.get('password')
            if password:
                user.set_password(password)
            user.save()
            
            # Update profile
            profile_form.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'User updated successfully!',
                'redirect_url': f'/user/detail/{user_id}/'
            })
        else:
            errors = {}
            if user_form.errors:
                errors.update(user_form.errors)
            if profile_form.errors:
                errors.update(profile_form.errors)
            
            return JsonResponse({
                'status': 'error',
                'errors': errors
            }, status=400)
    
    user_form = UserForm(instance=user)
    profile_form = UserProfileForm(instance=profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'user_data': user,
        'mode': 'edit'
    }
    
    return render(request, 'user_form.html', context)

@login_required
@user_passes_test(is_admin)
@csrf_exempt
def user_delete(request, user_id):
    """Delete a user"""
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        
        # Prevent admin from deleting themselves
        if user.id == request.user.id:
            return JsonResponse({
                'status': 'error',
                'message': 'You cannot delete your own account!'
            }, status=400)
        
        username = user.username
        user.delete()
        
        return JsonResponse({
            'status': 'success',
            'message': f'User {username} deleted successfully!',
            'redirect_url': '/user/list/'
        })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=400)

@login_required
@user_passes_test(is_admin)
@csrf_exempt
def user_toggle_status(request, user_id):
    """Toggle user active status"""
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        
        # Prevent admin from deactivating themselves
        if user.id == request.user.id:
            return JsonResponse({
                'status': 'error',
                'message': 'You cannot deactivate your own account!'
            }, status=400)
        
        user.is_active = not user.is_active
        user.save()
        
        status = 'activated' if user.is_active else 'deactivated'
        
        return JsonResponse({
            'status': 'success',
            'message': f'User {user.username} {status} successfully!',
            'is_active': user.is_active
        })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=400)