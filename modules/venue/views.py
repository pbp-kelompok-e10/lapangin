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



def search_venue(request):
    locations = Venue.objects.values('city', 'country').distinct().order_by('city')
    
    capacity_ranges = [
        {'value': '', 'label': 'Semua Kapasitas'},
        {'value': '0-10000', 'label': '0 - 10.000 Kursi'},
        {'value': '10001-20000', 'label': '10.001 - 20.000 Kursi'},
        {'value': '20001-50000', 'label': '20.001 - 50.000 Kursi'},
        {'value': '50001+', 'label': '50.001+ Kursi'},
    ]
    
    query = request.GET.get('q', '')  
    capacity = request.GET.get('capacity', '')  
    max_price = request.GET.get('max_price', '') 
    location_filter = request.GET.get('location', '')  
    capacity_filter = request.GET.get('capacity', '') 

    

    venues = Venue.objects.all()

    venues_data = [
        {
            'id': venue.id,
            'stadium': venue.name,
            'city': venue.city,
            'country': venue.country,
            'capacity': venue.capacity,
            'thumbnail': venue.thumbnail,
            'price': float(venue.price),  
            'description': venue.description if venue.description else 'Stadion modern dengan fasilitas lengkap untuk berbagai acara olahraga.',
            'owner_id': str(venue.owner.id) if venue.owner else '',
            'can_access_management': is_venue_provider_or_admin(request.user),
            'is_owner': (str(request.user.id) == str(venue.owner.id)) if request.user.is_authenticated and venue.owner else False
            }
            for venue in venues
        ]

    can_add_venue = is_venue_provider_or_admin(request.user)
    
    return render(request, 'venue/search_venue.html', {
        'venues': json.dumps(venues_data),
        'query': query,
        'capacity': capacity,
        'max_price': max_price,
        'selected_location': location_filter,
        'selected_capacity': capacity_filter,
        'locations': locations, 
        'capacity_ranges': capacity_ranges, 
        'user': request.user  
    })

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
    """
    Menangani pembuatan Venue baru. Hanya dapat diakses oleh user yang
    merupakan staff/admin atau memiliki atribut is_venue_provider=True.
    """
    
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
    """
    Menangani penghapusan Venue. Hanya pemilik/admin yang bisa menghapus.
    """
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


# @csrf_exempt
# def import_venues(request):
#     if not request.user.is_authenticated or not request.user.is_staff:
#         return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)

#     if request.method == 'POST':
#         csv_file = request.FILES.get('csv_file')
#         if not csv_file or not csv_file.name.endswith('.csv'):
#             return JsonResponse({'success': False, 'error': 'File harus berupa CSV'})

#         fs = FileSystemStorage()
#         filename = fs.save(csv_file.name, csv_file)
#         file_path = fs.path(filename)

#         try:
#             with open(file_path, 'r', encoding='utf-8') as file:
#                 reader = csv.DictReader(file)
#                 required_columns = {'stadium', 'city', 'country', 'capacity'}
#                 if not all(col.lower() in [c.lower() for c in reader.fieldnames] for col in required_columns):
#                     fs.delete(filename)
#                     return JsonResponse({'success': False, 'error': 'CSV harus memiliki kolom: stadium, city, country, capacity'})

#                 Venue.objects.all().delete()

#                 for row in reader:
#                     price_value = row.get('price', row.get('Price', ''))
#                     price = float(price_value) 

#                     Venue.objects.create(
#                         name=row.get('stadium', row.get('Stadium', '')),
#                         city=row.get('city', row.get('City', '')),
#                         country=row.get('country', row.get('Country', '')),
#                         capacity=int(row.get('capacity', row.get('Capacity', 0))),
#                         price=price,  
#                         rating=float(row.get('rating', 4.0)) if row.get('rating') else None,
#                         thumbnail=row.get('thumbnail', row.get('Thumbnail', 'img/default_venue.jpg')),
#                         description=row.get('description', row.get('Description', 'Stadion modern dengan fasilitas lengkap.'))
#                     )
#             fs.delete(filename)
#             return JsonResponse({'success': True, 'message': 'Dataset berhasil diimpor'})
#         except Exception as e:
#             fs.delete(filename)
#             return JsonResponse({'success': False, 'error': str(e)})


#     return render(request, 'import_venues.html')