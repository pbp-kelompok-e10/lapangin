import json
import csv
from django.shortcuts import render
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
from modules.venue.models import Venue

def search_venue(request):
    # Ambil nilai unik untuk dropdown lokasi (City, Country) - dipertahankan meskipun tidak digunakan di JS
    locations = Venue.objects.values('city', 'country').distinct().order_by('city')
    
    # Define capacity ranges for dropdown - dipertahankan meskipun diatur di JS
    capacity_ranges = [
        {'value': '', 'label': 'Semua Kapasitas'},
        {'value': '0-10000', 'label': '0 - 10.000 Kursi'},
        {'value': '10001-20000', 'label': '10.001 - 20.000 Kursi'},
        {'value': '20001-50000', 'label': '20.001 - 50.000 Kursi'},
        {'value': '50001+', 'label': '50.001+ Kursi'},
    ]
    
    # Pertahankan variabel dari request.GET
    query = request.GET.get('q', '')  # Kata kunci pencarian (tidak digunakan di server)
    capacity = request.GET.get('capacity', '')  # Filter kapasitas (tidak digunakan di server)
    max_price = request.GET.get('max_price', '')  # Filter harga (tidak digunakan di server)
    location_filter = request.GET.get('location', '')  # Filter lokasi (tidak digunakan di server)
    capacity_filter = request.GET.get('capacity', '')  # Filter kapasitas (tidak digunakan di server)

    # Ambil semua venue dari database (filter dilakukan di JavaScript)
    venues = Venue.objects.all()

    # Format data untuk template search.html
    venues_data = [
        {
            'id': venue.id,
            'stadium': venue.name,
            'city': venue.city,
            'country': venue.country,
            'capacity': venue.capacity,
            'thumbnail': venue.thumbnail,
            'price': float(venue.price),  
            'description': venue.description if venue.description else 'Stadion modern dengan fasilitas lengkap untuk berbagai acara olahraga.' 
            }
            for venue in venues
        ]

    return render(request, 'venue/search_venue.html', {
        'venues': json.dumps(venues_data),
        'query': query,
        'capacity': capacity,
        'max_price': max_price,
        'selected_location': location_filter,
        'selected_capacity': capacity_filter,
        'locations': locations,  # Dipertahankan meskipun tidak digunakan
        'capacity_ranges': capacity_ranges  # Dipertahankan meskipun tidak digunakan
    })

def venue_detail(request, venue_id):
    # Logika untuk mengambil data dari database
    venues = [
        {'id': v.id, 'stadium': v.name, 'city': v.city, 'country': v.country, 'capacity': v.capacity, 'price': v.price, 'thumbnail': v.thumbnail}
        for v in Venue.objects.all()  # Ganti dengan model Anda
    ]
    venue = next((v for v in venues if v['id'] == venue_id), None)
    if venue:
        return render(request, 'venue/venue_detail.html', {'selected_venue': venue, 'venues': venues})
    else:
        return render(request, 'venue/venue_detail.html', {'error': 'Stadion tidak ditemukan'}, status=404)
    
@csrf_exempt
def import_venues(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)

    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file')
        if not csv_file or not csv_file.name.endswith('.csv'):
            return JsonResponse({'success': False, 'error': 'File harus berupa CSV'})

        fs = FileSystemStorage()
        filename = fs.save(csv_file.name, csv_file)
        file_path = fs.path(filename)

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                required_columns = {'stadium', 'city', 'country', 'capacity'}
                if not all(col.lower() in [c.lower() for c in reader.fieldnames] for col in required_columns):
                    fs.delete(filename)
                    return JsonResponse({'success': False, 'error': 'CSV harus memiliki kolom: stadium, city, country, capacity'})

                # Kosongkan database sebelum impor
                Venue.objects.all().delete()

                for row in reader:
                    # Ambil price dari CSV jika ada, gunakan generate_fixed_price() sebagai fallback
                    price_value = row.get('price', row.get('Price', ''))
                    price = float(price_value) 

                    Venue.objects.create(
                        name=row.get('stadium', row.get('Stadium', '')),
                        city=row.get('city', row.get('City', '')),
                        country=row.get('country', row.get('Country', '')),
                        capacity=int(row.get('capacity', row.get('Capacity', 0))),
                        price=price,  
                        rating=float(row.get('rating', 4.0)) if row.get('rating') else None,
                        thumbnail=row.get('thumbnail', row.get('Thumbnail', 'img/default_venue.jpg')),
                        description=row.get('description', row.get('Description', 'Stadion modern dengan fasilitas lengkap.'))
                    )
            fs.delete(filename)
            return JsonResponse({'success': True, 'message': 'Dataset berhasil diimpor'})
        except Exception as e:
            fs.delete(filename)
            return JsonResponse({'success': False, 'error': str(e)})


    return render(request, 'import_venues.html')