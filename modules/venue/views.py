from django.shortcuts import render
from django.db.models import Q
from modules.venue.models import Venue

def search_venue(request):
    query = request.GET.get('q', '')  # Kata kunci pencarian (misalnya kota atau stadion)
    capacity = request.GET.get('capacity', '')  # Filter kapasitas
    max_price = request.GET.get('max_price', '')  # Filter harga

    # Ambil semua venue dari database
    venues = Venue.objects.all()

    # Filter berdasarkan kota atau nama stadion
    if query:
        venues = venues.filter(
            Q(city__icontains=query) | Q(name__icontains=query)
        )

    # Filter berdasarkan kapasitas
    if capacity:
        try:
            capacity = int(capacity.replace(',', ''))  # Hapus koma jika ada
            venues = venues.filter(capacity__gte=capacity)
        except ValueError:
            pass

    # Filter berdasarkan harga
    if max_price:
        try:
            max_price = float(max_price)
            venues = venues.filter(price__lte=max_price)
        except ValueError:
            pass

    # Format data untuk template
    venues_data = [
        {
            "name": venue.name,
            "location": f"{venue.city}, {venue.country}",
            "rating": venue.rating if hasattr(venue, 'rating') else 4.0,  # Default rating
            "capacity": f"{venue.capacity:,} Kursi",  # Format dengan koma
            "price": float(venue.price) if venue.price is not None else 0.00,  # Handle NULL
            "image": venue.image if hasattr(venue, 'image') else "img/default_venue.jpg",  # Default image
            "description": venue.description
        }
        for venue in venues
    ]

    return render(request, "venue/search_venue.html", {
        "venues": venues_data,
        "query": query,
        "capacity": capacity,
        "max_price": max_price
    })

def book_venue(request, venue_id):
    # Placeholder for booking functionality
    venue = Venue.objects.get(id=venue_id)
    return render(request, "venue/book_venue.html", {"venue_id": venue_id, "venue_name": venue.name})