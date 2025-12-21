import json
import csv
import random
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.core.files.storage import FileSystemStorage
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from modules.venue.models import Venue
from modules.venue.forms import VenueForm
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST

def search_venue(request):
    locations = Venue.objects.values('city', 'country').distinct().order_by('city')
    
    context = {
        'locations_json': json.dumps(list(locations)),
        
        'can_add_venue': request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff),
    }
    return render(request, 'venue/search_venue.html', context)

def venue_detail(request, venue_id):
    try:
        venue_exists = Venue.objects.filter(pk=venue_id).exists()
        if not venue_exists:
            return render(request, 'venue/venue_not_found.html', {'venue_id': venue_id}, status=404)

        is_admin = request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff)

        context = {
            'venue_id': venue_id,
            'is_admin': is_admin
        }
        return render(request, 'venue/venue_detail.html', context)
    except (ValueError, TypeError):
        return render(request, 'venue/venue_not_found.html', {'venue_id': 'invalid'}, status=400)

def get_venue_detail_api(request, venue_id):
    try:
        venue = Venue.objects.get(pk=venue_id)
        venue_data = {
            'id': venue.id,
            'stadium': venue.name,
            'city': venue.city,
            'country': venue.country,
            'capacity': venue.capacity,
            'price': venue.price,
            'thumbnail': venue.thumbnail if venue.thumbnail else '',
            'rating': venue.rating,
            'description': venue.description or "Deskripsi tidak tersedia.",
            'facilities': venue.facilities or "",
            'rules': venue.rules or "",
        }
        return JsonResponse({'success': True, 'venue': venue_data, 'is_authenticated': request.user.is_authenticated})
    except Venue.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Venue tidak ditemukan.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@login_required
@require_POST
def create_venue(request):
    form = VenueForm(request.POST)
    
    if not (request.user.is_authenticated or request.user.is_superuser or request.user.is_staff):
        return JsonResponse({'success': False, 'message': 'Anda tidak punya izin.'}, status=403)


    if form.is_valid():
        venue = form.save(commit=False)
        venue.owner = request.user
        venue.save()
        return JsonResponse({'success': True, 'message': 'Venue berhasil ditambahkan.'})
    else:
        return JsonResponse({'success': False, 'errors': form.errors.as_json()}, status=400)

@login_required
def edit_venue(request, venue_id):
    venue = get_object_or_404(Venue, pk=venue_id)

    if not (request.user.is_staff or venue.owner == request.user):
        return JsonResponse({'success': False, 'message': 'Anda tidak punya izin.'}, status=403)

    if request.method == 'POST':
        form = VenueForm(request.POST, instance=venue)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Venue berhasil diupdate.'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors.as_json()}, status=400)
    
    else:
        venue_data = {
            'stadium': venue.name,
            'city': venue.city,
            'country': venue.country,
            'capacity': venue.capacity,
            'price': venue.price,
            'thumbnail': venue.thumbnail,
            'description': venue.description,
            'facilities': venue.facilities,
            'rules': venue.rules,
        }
        return JsonResponse({'success': True, 'data': venue_data})

@login_required
@require_POST
def delete_venue(request, venue_id):
    venue = get_object_or_404(Venue, pk=venue_id)
    
    if not (request.user.is_superuser or venue.owner == request.user or request.user.is_staff):
            return JsonResponse({'success': False, 'message': 'Anda tidak memiliki izin untuk menghapus venue ini.'}, status=403)

    try:
        venue_name = venue.name
        venue.delete()
        return JsonResponse({'success': True, 'message': f'Venue "{venue_name}" berhasil dihapus.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

def search_venues_api(request):
    venues_list = Venue.objects.select_related('owner').all()
    # Filtering
    search_term = request.GET.get('search', '').strip()
    if search_term:
        venues_list = venues_list.filter(name__icontains=search_term)

    city = request.GET.get('city', '').strip()
    if city:
        venues_list = venues_list.filter(city=city)
        
    # Filter Kapasitas
    try:
        capacity_min = int(request.GET.get('capacity_min', 0))
        if capacity_min > 0:
            venues_list = venues_list.filter(capacity__gte=capacity_min)
    except (ValueError, TypeError):
        pass

    try:
        capacity_max = int(request.GET.get('capacity_max', 0))
        if capacity_max > 0:
            venues_list = venues_list.filter(capacity__lte=capacity_max)
    except (ValueError, TypeError):
        pass

    # Sorting
    sort_order = request.GET.get('sort', 'lowToHigh')
    if sort_order == 'highToLow':
        venues_list = venues_list.order_by('-price')
    else:
        venues_list = venues_list.order_by('price')

    paginator = Paginator(venues_list, 18) # 18 item per halaman
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    venues_data = []
    for venue in page_obj:
        venues_data.append({
            'id': venue.id,
            'stadium': venue.name,
            'city': venue.city,
            'country': venue.country,
            'capacity': venue.capacity,
            'price': venue.price,
            'thumbnail': venue.thumbnail if venue.thumbnail else '',
            'description': venue.description if venue.description else 'Deskripsi tidak tersedia',
            'rating': venue.rating,
            'can_access_management': (request.user.is_authenticated and
                                    (request.user.is_superuser or request.user == venue.owner or request.user.is_staff)),
            'url_detail': reverse('venue:venue_detail', args=[venue.id]),
            'url_edit': reverse('venue:edit_venue', args=[venue.id]),
            'url_delete': reverse('venue:delete_venue', args=[venue.id]),
        })

    return JsonResponse({
        'is_authenticated': request.user.is_authenticated,
        'venues': venues_data,
        'has_next_page': page_obj.has_next(),
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
    })

def show_json(request):
    venue_list = Venue.objects.all()
    data = [
        {
            'id': venue.id,
            'stadium': venue.name,
            'city': venue.city,
            'country': venue.country,
            'capacity': venue.capacity,
            'price': venue.price,
            'thumbnail': venue.thumbnail if venue.thumbnail else '',
            'rating': venue.rating,
            'description': venue.description or "Deskripsi tidak tersedia.",
            'facilities': venue.facilities or "",
            'rules': venue.rules or "",
        }
        for venue in venue_list
    ]
    return JsonResponse(data, safe=False)

def get_venues_api(request):
    try:
        venues_list = Venue.objects.all()
        venues_data = []
        for venue in venues_list:
            venues_data.append({
                'id': venue.id,
                'stadium': venue.name,
                'city': venue.city,
                'country': venue.country,
                'capacity': venue.capacity,
                'price': venue.price,
                'thumbnail': venue.thumbnail if venue.thumbnail else '',
                'rating': venue.rating,
                'facilities': venue.facilities or "",
                'rules': venue.rules or "",
                'url_detail': reverse('venue:venue_detail', args=[venue.id]),
            })

        return JsonResponse({
            'success': True,
            'venues': venues_data,
            'message': 'Venue berhasil dimuat.'
        })

    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Gagal memuat venue: {str(e)}'}, status=500)

def get_recommended_detail_api(request):
    try:

        venues_list = Venue.objects.all().order_by('-rating', '-id')[:2]
        venues_data = []
        for venue in venues_list:
            venues_data.append({
                'id': venue.id,
                'stadium': venue.name,
                'city': venue.city,
                'country': venue.country,
                'price': venue.price,
                'capacity': venue.capacity,
                'thumbnail': venue.thumbnail if venue.thumbnail else '',
                'rating': venue.rating,
                'url_detail': reverse('venue:venue_detail', args=[venue.id]),
            })

        return JsonResponse({
            'success': True,
            'venues': venues_data,
            'message': 'Rekomendasi venue berhasil dimuat.'
        })

    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Gagal memuat rekomendasi: {str(e)}'}, status=500)

def get_recommended_venues_api(request):
    try:

        venues_list = Venue.objects.all().order_by('-rating', '-id')[:2]
        venues_data = []
        for venue in venues_list:
            venues_data.append({
                'id': venue.id,
                'stadium': venue.name,
                'city': venue.city,
                'country': venue.country,
                'capacity': venue.capacity,
                'price': venue.price,
                'thumbnail': venue.thumbnail if venue.thumbnail else '',
                'rating': venue.rating,
                'url_detail': reverse('venue:venue_detail', args=[venue.id]),
            })

        return JsonResponse({
            'success': True,
            'venues': venues_data,
            'message': 'Rekomendasi venue berhasil dimuat.'
        })

    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Gagal memuat rekomendasi: {str(e)}'}, status=500)

def check_venue_creation_permission_api(request):

    is_allowed = request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff)

    return JsonResponse({

        'can_create_venue': is_allowed

    })


def get_flutter_user_info(user):
    """Helper function to get user info for Flutter"""
    if not user.is_authenticated:
        return None
    return {
        'user_id': user.id,
        'username': user.username,
        'is_authenticated': True,
        'is_superuser': user.is_superuser,
        'is_staff': user.is_staff,
        'is_admin': user.is_superuser or user.is_staff,
    }


@csrf_exempt
def create_venue_flutter(request):
    if request.method != 'POST':
        return JsonResponse({"status": "error", "message": "Method tidak diizinkan."}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse(
            {"status": "error", "message": "Harap login untuk membuat venue. Akses ditolak.", "user": None},
            status=403
        )
    
    # Check if user is admin (superuser or staff)
    is_admin = request.user.is_superuser or request.user.is_staff
    if not is_admin:
        return JsonResponse(
            {"status": "error", "message": "Hanya admin yang dapat membuat venue.", "user": get_flutter_user_info(request.user)},
            status=403
        )
        
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON format."}, status=400)

    form = VenueForm(data)

    if form.is_valid():
        venue = form.save(commit=False)
        venue.owner = request.user
        venue.save()
        return JsonResponse({
            'status': 'success', 
            'message': 'Venue berhasil ditambahkan.',
            'user': get_flutter_user_info(request.user),
            'venue_id': str(venue.id)
        }, status=201)
    else:
        error_details = json.loads(form.errors.as_json())
        return JsonResponse({'status': 'error', 'errors': error_details, 'user': get_flutter_user_info(request.user)}, status=400)

@csrf_exempt
def edit_venue_flutter(request, venue_id):
    if request.method != 'POST':
        return JsonResponse({"status": "error", "message": "Method tidak diizinkan."}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse(
            {"status": "error", "message": "Harap login untuk edit venue. Akses ditolak.", "user": None},
            status=403
        )

    venue = get_object_or_404(Venue, pk=venue_id)
    
    # Check if user is admin OR owner of the venue
    is_admin = request.user.is_superuser or request.user.is_staff
    is_owner = venue.owner == request.user
    
    if not (is_admin or is_owner):
        return JsonResponse(
            {"status": "error", "message": "Anda tidak memiliki izin untuk mengedit venue ini.", "user": get_flutter_user_info(request.user)},
            status=403
        )
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON format."}, status=400)
    
    form = VenueForm(data, instance=venue)
    if form.is_valid():
        venue = form.save(commit=False)
        # Don't change owner on edit
        venue.save()
        return JsonResponse({
            'status': 'success', 
            'message': 'Venue berhasil diedit.',
            'user': get_flutter_user_info(request.user),
            'venue_id': str(venue.id)
        }, status=200)
    else:
        error_details = json.loads(form.errors.as_json())
        return JsonResponse({'status': 'error', 'errors': error_details, 'user': get_flutter_user_info(request.user)}, status=400)

@csrf_exempt
def delete_venue_api(request, venue_id):
    venue = get_object_or_404(Venue, pk=venue_id)
    
    if not request.user.is_authenticated:
        return JsonResponse({
            'status': 'error', 
            'message': 'Anda harus login untuk menghapus venue.',
            'user': None
        }, status=403)
    
    # Check if user is admin OR owner of the venue
    is_admin = request.user.is_superuser or request.user.is_staff
    is_owner = venue.owner == request.user
    
    if not (is_admin or is_owner):
        return JsonResponse({
            'status': 'error', 
            'message': 'Anda tidak memiliki izin untuk menghapus venue ini.',
            'user': get_flutter_user_info(request.user)
        }, status=403)

    try:
        venue_name = venue.name
        venue_id_deleted = str(venue.id)
        venue.delete()
        return JsonResponse({
            'status': 'success',
            'message': f'Venue "{venue_name}" berhasil dihapus.',
            'user': get_flutter_user_info(request.user),
            'deleted_venue_id': venue_id_deleted
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        