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

def search_venue(request):
    locations = Venue.objects.values('city', 'country').distinct().order_by('city')
    
    context = {
        'locations_json': json.dumps(list(locations)),
        
        'can_add_venue': request.user.is_authenticated
    }
    return render(request, 'venue/search_venue.html', context)

def venue_detail(request, venue_id):
    venues = [
        {'id': v.id, 'stadium': v.name, 'city': v.city, 'country': v.country, 'capacity': v.capacity, 'price': v.price, 'thumbnail': v.thumbnail}
        for v in Venue.objects.all()
    ]
    venue = next((v for v in venues if v['id'] == venue_id), None)
    if venue:
        return render(request, 'venue/venue_detail.html', {'selected_venue': venue, 'venues': venues})
    else:
        return render(request, 'venue/venue_detail.html', {'error': 'Stadion tidak ditemukan'}, status=404)

@login_required
@venue_access_required
def create_venue(request):
    form = VenueForm(request.POST or None)
    
    if request.method == 'POST':
        if form.is_valid():
            User = get_user_model()
            venue = form.save(commit=False)
            
            venue.owner = request.user
            venue.save()
            
            messages.success(request, 'Venue berhasil ditambahkan!')
            return redirect('venue:search_venue')
        else:
            messages.error(request, 'Gagal menambahkan Venue. Silakan periksa kembali data Anda.')

    context = {
        'form': form
    }
    return render(request, 'venue/create_venue.html', context)


@login_required
@venue_access_required
def edit_venue(request, venue_id):
    """
    Menangani pengeditan Venue yang sudah ada. Hanya pemilik/admin yang bisa mengedit.
    """
    venue = get_object_or_404(Venue, pk=venue_id)
    
    if not (request.user.is_staff or venue.owner == request.user):
        messages.error(request, 'Anda tidak memiliki izin untuk mengedit venue ini.')
        return redirect('venue:search_venue')

    form = VenueForm(request.POST or None, instance=venue)
    
    if form.is_valid() and request.method == 'POST':
        form.save()
        messages.success(request, 'Venue berhasil diupdate.')
        return redirect('venue:search_venue')

    context = {
        'form': form,
        'venue': venue
    }

    return render(request, "venue/edit_venue.html", context)


@login_required
@venue_access_required
def delete_venue(request, venue_id):
    venue = get_object_or_404(Venue, pk=venue_id)
    
    if not (request.user.is_staff or venue.owner == request.user):
        messages.error(request, 'Anda tidak memiliki izin untuk menghapus venue ini.')
        return redirect('venue:search_venue')
    
    if request.method == 'POST':
        venue.delete()
        messages.success(request, 'Venue berhasil dihapus.')
        return redirect('venue:search_venue')
    
    messages.error(request, 'Permintaan hapus tidak valid.')
    return redirect('venue:search_venue')

def search_venues_api(request):
    venues_list = Venue.objects.select_related('owner').all()
    # Filtering
    search_term = request.GET.get('search', '').strip()
    if search_term:
        venues_list = venues_list.filter(stadium__icontains=search_term)

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
