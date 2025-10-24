from django.shortcuts import render

@require_GET
def get_booked_dates_api(request, venue_id):
    if not Venue.objects.filter(pk=venue_id).exists():
        return JsonResponse({'error': 'Venue not found.'}, status=404)

    bookings = Booking.objects.filter(venue_id=venue_id, end_date__gte=date.today())

    booked_dates = []
    for booking in bookings:
        booked_dates.append({
            'from': booking.start_date.isoformat(),
            'to': booking.end_date.isoformat()
        })
        

    return JsonResponse({'booked_dates': booked_dates})

@login_required
@require_POST
def create_booking_api(request):
    try:
        data = json.loads(request.body)
        venue_id = data.get('venue_id')
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')

        if not all([venue_id, start_date_str, end_date_str]):
            return JsonResponse({'success': False, 'message': 'Data tidak lengkap.'}, status=400)

        venue = get_object_or_404(Venue, pk=venue_id)
        start_date = date.fromisoformat(start_date_str)
        end_date = date.fromisoformat(end_date_str)

        if start_date < date.today():
            return JsonResponse({'success': False, 'message': 'Tanggal mulai tidak boleh di masa lalu.'}, status=400)
        if end_date < start_date:
            return JsonResponse({'success': False, 'message': 'Tanggal selesai harus setelah tanggal mulai.'}, status=400)

        overlapping_bookings = Booking.objects.filter(
            venue=venue,
            start_date__lte=end_date,
            end_date__gte=start_date
        )

        if overlapping_bookings.exists():
            return JsonResponse({'success': False, 'message': 'Tanggal yang dipilih sudah dibooking sebagian atau seluruhnya.'}, status=400)

        booking = Booking.objects.create(
            user=request.user,
            venue=venue,
            start_date=start_date,
            end_date=end_date
        )

        return JsonResponse({
            'success': True,
            'message': 'Booking berhasil dibuat!',
            'booking_details': {
                'id': booking.id,
                'venue': booking.venue.name,
                'start': booking.start_date.isoformat(),
                'end': booking.end_date.isoformat(),
            }
        })

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Format data tidak valid.'}, status=400)
    except ValueError:
        return JsonResponse({'success': False, 'message': 'Format tanggal tidak valid (YYYY-MM-DD).'}, status=400)
    except Venue.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Venue tidak ditemukan.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Terjadi kesalahan server: {str(e)}'}, status=500)