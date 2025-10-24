from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
from .models import Booking
from modules.venue.models import Venue
import json
from datetime import date
from django.db.models import F

@require_GET
def get_booked_dates_api(request, venue_id):
    """ Returns a list of booked dates (YYYY-MM-DD strings) for a venue. """
    if not Venue.objects.filter(pk=venue_id).exists():
        return JsonResponse({'error': 'Venue not found.'}, status=404)

    booked_dates = Booking.objects.filter(
        venue_id=venue_id,
        booking_date__gte=date.today()
    ).values_list('booking_date', flat=True)

    booked_date_strings = [d.isoformat() for d in booked_dates]

    return JsonResponse({'booked_dates': booked_date_strings})


@login_required
@require_POST
def create_booking_api(request):
    """ Creates a new single-day booking. """
    try:
        data = json.loads(request.body)
        venue_id = data.get('venue_id')
        date_str = data.get('booking_date')

        if not all([venue_id, date_str]):
            return JsonResponse({'success': False, 'message': 'Data tidak lengkap (venue_id, booking_date).'}, status=400)

        venue = get_object_or_404(Venue, pk=venue_id)
        booking_date = date.fromisoformat(date_str)

        # Validation
        if booking_date < date.today():
            return JsonResponse({'success': False, 'message': 'Tanggal booking tidak boleh di masa lalu.'}, status=400)

        # Check if already booked (using unique_together implicitly helps, but explicit check is clearer)
        if Booking.objects.filter(venue=venue, booking_date=booking_date).exists():
            return JsonResponse({'success': False, 'message': 'Tanggal ini sudah dibooking.'}, status=400)

        # Create Booking
        booking = Booking.objects.create(
            user=request.user,
            venue=venue,
            booking_date=booking_date
        )

        return JsonResponse({
            'success': True,
            'message': 'Booking berhasil dibuat!',
            'booking_details': {
                'id': booking.id,
                'venue': booking.venue.name,
                'date': booking.booking_date.isoformat(),
            }
        })

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Format data tidak valid.'}, status=400)
    except ValueError:
        return JsonResponse({'success': False, 'message': 'Format tanggal tidak valid (YYYY-MM-DD).'}, status=400)
    except Venue.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Venue tidak ditemukan.'}, status=404)
    except Exception as e:
        # Catch potential IntegrityError from unique_together if race condition occurs
        if 'UNIQUE constraint failed' in str(e):
            return JsonResponse({'success': False, 'message': 'Tanggal ini sudah dibooking.'}, status=400)
        return JsonResponse({'success': False, 'message': f'Terjadi kesalahan server: {str(e)}'}, status=500)


@login_required
def booking_history_page(request):
    """ Renders the booking history page shell. """
    return render(request, 'booking/booking_history.html')

@login_required
def get_user_bookings_api(request):
    """ Returns a list of bookings for the current user. """
    user_bookings = Booking.objects.filter(user=request.user).select_related('venue').order_by('-booking_date') 

    bookings_data = []
    for booking in user_bookings:
        bookings_data.append({
            'booking_id': booking.id,
            'venue_id': booking.venue.id,
            'venue_name': booking.venue.name,
            'venue_thumbnail': booking.venue.thumbnail if booking.venue.thumbnail else '/static/img/default-thumbnail.jpg',
            'booking_date': booking.booking_date.isoformat(),
            'created_at': booking.created_at.isoformat(),
        })

    return JsonResponse({'bookings': bookings_data})