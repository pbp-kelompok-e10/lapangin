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
from .decorators import venue_access_required
from .decorators import is_venue_provider_or_admin
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST

def search_venue(request):
    locations = Venue.objects.values('city', 'country').distinct().order_by('city')
    
    context = {
        'locations_json': json.dumps(list(locations)),
        
        'can_add_venue': request.user.is_authenticated
    }
    return render(request, 'venue/search_venue.html', context)

def venue_detail(request, venue_id):
    try:
        venue_exists = Venue.objects.filter(pk=int(venue_id)).exists()
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
            'thumbnail': venue.thumbnail if venue.thumbnail else '/static/img/default-thumbnail.jpg',
            'rating': venue.rating,
            'description': venue.description or "Deskripsi tidak tersedia.",
        }
        return JsonResponse({'success': True, 'venue': venue_data})
    except Venue.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Venue tidak ditemukan.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@login_required
@venue_access_required
@require_POST
def create_venue(request):
    form = VenueForm(request.POST)
    
    if form.is_valid():
        venue = form.save(commit=False)
        venue.owner = request.user
        venue.save()
        return JsonResponse({'success': True, 'message': 'Venue berhasil ditambahkan.'})
    else:
        return JsonResponse({'success': False, 'errors': form.errors.as_json()}, status=400)

@login_required
@venue_access_required
def edit_venue(request, venue_id):
    venue = get_object_or_404(Venue, pk=venue_id)

    if not (request.user.is_superuser or venue.owner == request.user):
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
        }
        return JsonResponse({'success': True, 'data': venue_data})

@login_required
@venue_access_required
@require_POST
def delete_venue(request, venue_id):
    venue = get_object_or_404(Venue, pk=venue_id)
    
    if not (request.user.is_superuser or venue.owner == request.user):
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
            'thumbnail': venue.thumbnail if venue.thumbnail else '/static/img/default-thumbnail.jpg',
            'rating': venue.rating,
            'can_access_management': (request.user.is_authenticated and
                                    (request.user.is_superuser or request.user == venue.owner)),
            
            'url_detail': reverse('venue:venue_detail', args=[venue.id]),
            'url_edit': reverse('venue:edit_venue', args=[venue.id]),
            'url_delete': reverse('venue:delete_venue', args=[venue.id]),
        })

    return JsonResponse({
        'venues': venues_data,
        'has_next_page': page_obj.has_next(),
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
    })
