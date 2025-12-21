from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q
from .models import UserProfile
from .forms import UserForm, UserProfileForm
import json


# ========== HELPER FUNCTIONS ==========

def is_admin(user):
    """Check if user is admin (staff or superuser)"""
    return user.is_staff or user.is_superuser


def api_login_required(view_func):
    """Decorator that returns JSON error for unauthenticated API requests"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({
                'status': 'error',
                'message': 'Authentication required. Please log in.'
            }, status=401)
        return view_func(request, *args, **kwargs)
    return wrapper


def api_admin_required(view_func):
    """Decorator that returns JSON error for non-admin API requests"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({
                'status': 'error',
                'message': 'Authentication required. Please log in.'
            }, status=401)
        if not (request.user.is_staff or request.user.is_superuser):
            return JsonResponse({
                'status': 'error',
                'message': 'Admin access required.'
            }, status=403)
        return view_func(request, *args, **kwargs)
    return wrapper


# ========== WEB VIEWS (Return HTML) ==========

@login_required
@user_passes_test(is_admin)
def user_list(request):
    """Display list of all users (HTML page)"""
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    users = User.objects.all().select_related('profile').order_by('-date_joined')
    
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)
    
    paginator = Paginator(users, 10)
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
    """View details of a specific user (HTML page)"""
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
    """Create a new user (HTML form page)"""
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            password = user_form.cleaned_data.get('password')
            if password:
                user.set_password(password)
            user.save()
            
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
    """Edit existing user (HTML form page)"""
    user = get_object_or_404(User, id=user_id)
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            password = user_form.cleaned_data.get('password')
            if password:
                user.set_password(password)
            user.save()
            
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


# ========== API ENDPOINTS FOR FLUTTER ==========

@csrf_exempt
@api_admin_required
def user_list_api(request):
    """API: Get list of users (JSON)"""
    if request.method != 'GET':
        return JsonResponse({
            'status': 'error',
            'message': 'Only GET method is allowed'
        }, status=405)
    
    try:
        search_query = request.GET.get('search', '')
        status_filter = request.GET.get('status', '')
        
        users = User.objects.all().select_related('profile').order_by('-date_joined')
        
        if search_query:
            users = users.filter(
                Q(username__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query)
            )
        
        if status_filter == 'active':
            users = users.filter(is_active=True)
        elif status_filter == 'inactive':
            users = users.filter(is_active=False)
        
        users_data = []
        for user in users:
            profile = getattr(user, 'profile', None)
            users_data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email or '',
                'name': f"{user.first_name} {user.last_name}".strip() or user.username,
                'is_authenticated': True,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'is_active': user.is_active,
                'date_joined': user.date_joined.isoformat() if user.date_joined else None,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'profile': {
                    'full_name': profile.full_name if profile else '',
                    'phone': profile.phone if profile else '',
                    'address': profile.address if profile else '',
                    'is_active': profile.is_active if profile else True,
                    'updated_at': profile.updated_at.isoformat() if profile and profile.updated_at else None,
                } if profile else None
            })
        
        return JsonResponse(users_data, safe=False)
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@api_admin_required
def user_create_api(request):
    """API: Create new user (JSON)"""
    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': 'Only POST method is allowed'
        }, status=405)
    
    try:
        # Parse JSON data
        try:
            if request.body:
                data = json.loads(request.body)
            else:
                data = {}
        except json.JSONDecodeError as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Invalid JSON: {str(e)}'
            }, status=400)
        
        # Extract fields
        username = data.get('username', '').strip()
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')
        full_name = data.get('full_name', '').strip()
        phone = data.get('phone', '').strip()
        address = data.get('address', '').strip()
        is_staff = data.get('is_staff', False)
        is_active = data.get('is_active', True)
        
        # Validation
        errors = {}
        
        if not username:
            errors['username'] = ['Username is required']
        elif User.objects.filter(username=username).exists():
            errors['username'] = ['Username already exists']
        
        if not password:
            errors['password'] = ['Password is required']
        elif len(password) < 6:
            errors['password'] = ['Password must be at least 6 characters']
        
        if password != confirm_password:
            errors['confirm_password'] = ['Passwords do not match']
        
        if errors:
            return JsonResponse({
                'status': 'error',
                'message': 'Validation failed',
                'errors': errors
            }, status=400)
        
        # Create user
        user = User.objects.create_user(
            username=username,
            password=password,
            is_staff=is_staff,
            is_active=is_active
        )
        
        # Split full name into first_name and last_name
        if full_name:
            name_parts = full_name.split(maxsplit=1)
            user.first_name = name_parts[0] if name_parts else ''
            user.last_name = name_parts[1] if len(name_parts) > 1 else ''
            user.save()
        
        # Create profile
        profile = UserProfile.objects.create(
            user=user,
            full_name=full_name,
            phone=phone,
            address=address,
            is_active=is_active
        )
        
        return JsonResponse({
            'status': 'success',
            'message': f'User {username} created successfully!',
            'user': {
                'id': user.id,
                'username': user.username,
                'is_staff': user.is_staff,
                'is_active': user.is_active
            }
        })
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Failed to create user: {str(e)}'
        }, status=500)


@csrf_exempt
@api_admin_required
def user_update_api(request, user_id):
    """API: Update user (JSON)"""
    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': 'Only POST method is allowed'
        }, status=405)
    
    try:
        user = get_object_or_404(User, id=user_id)
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        # Parse JSON data
        try:
            if request.body:
                data = json.loads(request.body)
            else:
                data = {}
        except json.JSONDecodeError as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Invalid JSON: {str(e)}'
            }, status=400)
        
        # Update user fields
        username = data.get('username')
        if username and username != user.username:
            if User.objects.filter(username=username).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Username already exists'
                }, status=400)
            user.username = username
        
        password = data.get('password', '').strip()
        if password:
            confirm_password = data.get('confirm_password', '')
            if password != confirm_password:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Passwords do not match'
                }, status=400)
            if len(password) < 6:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Password must be at least 6 characters'
                }, status=400)
            user.set_password(password)
        
        # Update profile fields
        full_name = data.get('full_name', '').strip()
        if full_name:
            profile.full_name = full_name
            name_parts = full_name.split(maxsplit=1)
            user.first_name = name_parts[0] if name_parts else ''
            user.last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        if 'phone' in data:
            profile.phone = data['phone']
        if 'address' in data:
            profile.address = data['address']
        if 'is_staff' in data:
            user.is_staff = bool(data['is_staff'])
        if 'is_active' in data:
            user.is_active = bool(data['is_active'])
            profile.is_active = bool(data['is_active'])
        
        user.save()
        profile.save()
        
        return JsonResponse({
            'status': 'success',
            'message': f'User {user.username} updated successfully!'
        })
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Failed to update user: {str(e)}'
        }, status=500)


@csrf_exempt
@api_admin_required
def user_delete_api(request, user_id):
    """API: Delete user (JSON)"""
    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': 'Only POST method is allowed'
        }, status=405)
    
    try:
        user = get_object_or_404(User, id=user_id)
        
        if user.id == request.user.id:
            return JsonResponse({
                'status': 'error',
                'message': 'You cannot delete your own account!'
            }, status=400)
        
        username = user.username
        user.delete()
        
        return JsonResponse({
            'status': 'success',
            'message': f'User {username} deleted successfully!'
        })
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Failed to delete user: {str(e)}'
        }, status=500)


@csrf_exempt
@api_admin_required
def user_toggle_status_api(request, user_id):
    """API: Toggle user active status (JSON)"""
    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': 'Only POST method is allowed'
        }, status=405)
    
    try:
        user = get_object_or_404(User, id=user_id)
        
        if user.id == request.user.id:
            return JsonResponse({
                'status': 'error',
                'message': 'You cannot deactivate your own account!'
            }, status=400)
        
        user.is_active = not user.is_active
        user.save()
        
        # Update profile if exists
        if hasattr(user, 'profile'):
            user.profile.is_active = user.is_active
            user.profile.save()
        
        status = 'activated' if user.is_active else 'deactivated'
        
        return JsonResponse({
            'status': 'success',
            'message': f'User {user.username} {status} successfully!',
            'is_active': user.is_active
        })
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Failed to toggle status: {str(e)}'
        }, status=500)


# ========== PROFILE API ENDPOINTS ==========

@csrf_exempt
@api_login_required
def get_profile(request):
    """API: Get current user's profile (JSON)"""
    if request.method != 'GET':
        return JsonResponse({
            'status': 'error',
            'message': 'Only GET method is allowed'
        }, status=405)
    
    try:
        user = request.user
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        data = {
            'id': user.id,
            'username': user.username,
            'email': user.email or '',
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'is_active': user.is_active,
            'date_joined': user.date_joined.isoformat() if user.date_joined else None,
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'profile': {
                'full_name': profile.full_name or '',
                'phone': profile.phone or '',
                'address': profile.address or '',
                'is_active': profile.is_active,
                'updated_at': profile.updated_at.isoformat() if profile.updated_at else None,
            }
        }
        
        return JsonResponse(data, safe=False)
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@api_login_required
def update_profile(request):
    """API: Update current user's profile (JSON)"""
    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': 'Only POST method is allowed'
        }, status=405)
    
    try:
        user = request.user
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        # Parse data
        try:
            if request.body:
                data = json.loads(request.body)
            else:
                data = request.POST.dict()
        except json.JSONDecodeError:
            data = request.POST.dict()
        
        # Update email
        email = data.get('email', '').strip()
        if email:
            user.email = email
            user.save()
        
        # Update profile
        full_name = data.get('full_name', '').strip()
        if full_name:
            profile.full_name = full_name
            name_parts = full_name.split(maxsplit=1)
            user.first_name = name_parts[0] if name_parts else ''
            user.last_name = name_parts[1] if len(name_parts) > 1 else ''
            user.save()
        
        profile.phone = data.get('phone', '').strip()
        profile.address = data.get('address', '').strip()
        profile.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Profile updated successfully!'
        })
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Failed to update profile: {str(e)}'
        }, status=500)