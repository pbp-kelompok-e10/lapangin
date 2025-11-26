from .models import Booking
from datetime import date
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST, require_GET, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from modules.venue.models import Venue
import json

@login_required
def booking_history_page(request):
    return render(request, 'booking_history.html')



@require_GET
def get_booked_dates_api(request, venue_id):
    if not Venue.objects.filter(pk=venue_id).exists():
        return JsonResponse({'error': 'Venue not found.'}, status=404)

    booked_dates = Booking.objects.filter(
        venue_id=venue_id,
        booking_date__gte=date.today()
    ).values_list('booking_date', flat=True)

    booked_date_strings = [d.isoformat() for d in booked_dates]

    return JsonResponse({'booked_dates': booked_date_strings})


@csrf_exempt # Disable CSRF for API endpoints consumed by non-browser clients
@require_POST
def create_booking_api(request):
    try:
        data = json.loads(request.body)
        venue_id = data.get('venue_id')
        date_str = data.get('booking_date')

        if not request.user.is_authenticated:
            return JsonResponse({
            'success': False,
            'message': 'Otentikasi diperlukan. Silakan login terlebih dahulu.'
        }, status=401)

        if not all([venue_id, date_str]):
            return JsonResponse({'success': False, 'message': 'Data tidak lengkap (venue_id, booking_date).'}, status=400)

        venue = get_object_or_404(Venue, pk=venue_id)
        booking_date = date.fromisoformat(date_str)

        # Validation
        if booking_date < date.today():
            return JsonResponse({'success': False, 'message': 'Tanggal booking tidak boleh di masa lalu.'}, status=400)

        # Check if already booked
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
        if 'UNIQUE constraint failed' in str(e):
            return JsonResponse({'success': False, 'message': 'Tanggal ini sudah dibooking.'}, status=400)
        return JsonResponse({'success': False, 'message': f'Terjadi kesalahan server: {str(e)}'}, status=500)


@csrf_exempt
def get_user_bookings_api(request):
    user_bookings = Booking.objects.filter(user=request.user).select_related('venue').order_by('-booking_date')
    bookings_data = []
    for booking in user_bookings:
        can_modify = booking.booking_date >= date.today()
        bookings_data.append({
            'booking_id': booking.id,
            'venue_id': booking.venue.id,
            'venue_name': booking.venue.name,
            'venue_thumbnail': booking.venue.thumbnail if booking.venue.thumbnail else '/static/img/default-thumbnail.jpg',
            'booking_date': booking.booking_date.isoformat(),
            'created_at': booking.created_at.isoformat(),
            'can_modify': can_modify,
            'url_detail': reverse('venue:venue_detail', args=[booking.venue.id]),
        })

    return JsonResponse({'bookings': bookings_data})


@csrf_exempt
@require_http_methods(["GET", "POST"])
def edit_booking_api(request, booking_id):
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': 'Authentication credentials were not provided.'
        }, status=401)
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)

    if booking.booking_date < date.today():
        return JsonResponse({'success': False, 'message': 'Booking yang sudah lewat tidak bisa diubah.'}, status=403)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_date_str = data.get('booking_date')
            if not new_date_str:
                return JsonResponse({'success': False, 'message': 'Tanggal baru diperlukan.'}, status=400)

            new_date = date.fromisoformat(new_date_str)

            if new_date < date.today():
                return JsonResponse({'success': False, 'message': 'Tanggal baru tidak boleh di masa lalu.'}, status=400)

            if Booking.objects.filter(
                venue=booking.venue,
                booking_date=new_date
            ).exclude(pk=booking.id).exists():
                return JsonResponse({'success': False, 'message': 'Tanggal baru tersebut sudah dibooking.'}, status=400)

            booking.booking_date = new_date
            booking.save(update_fields=['booking_date'])

            return JsonResponse({
                'success': True,
                'message': 'Tanggal booking berhasil diperbarui.',
                'updated_booking': {
                'booking_id': booking.id,
                'booking_date': booking.booking_date.isoformat(),
                }
            })

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Format data tidak valid.'}, status=400)
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Format tanggal baru tidak valid (YYYY-MM-DD).'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Terjadi kesalahan: {str(e)}'}, status=500)

    else:
        return JsonResponse({'success': True, 'data': {'booking_date': booking.booking_date.isoformat()}})


@csrf_exempt
@require_POST
def delete_booking_api(request, booking_id):
    """ Handles deleting a booking. """
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': 'Authentication credentials were not provided.'
        }, status=401)
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)

    if booking.booking_date < date.today():
        return JsonResponse({'success': False, 'message': 'Booking yang sudah lewat tidak bisa dihapus.'}, status=403)

    try:
        booking_id_deleted = booking.id
        venue_name = booking.venue.name
        booking_date = booking.booking_date
        booking.delete()
        return JsonResponse({
            'success': True,
            'message': f'Booking untuk {venue_name} pada tanggal {booking_date.isoformat()} berhasil dibatalkan.',
            'deleted_booking_id': booking_id_deleted
            })
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Gagal membatalkan booking: {str(e)}'}, status=500)
    