from django.shortcuts import render

from .models import Review
from ..venue.models import Venue
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

@login_required
@require_POST
def add_review(request):
    try:
        venue_id = request.POST.get('venue_id')
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '')

        if not venue_id or not rating:
            return JsonResponse({'status': 'error', 'message': 'Venue ID dan rating diperlukan.'}, status=400)

        venue = get_object_or_404(Venue, pk=int(venue_id))

        review, created = Review.objects.update_or_create(
            user=request.user,
            venue=venue,
            defaults={
                'rating': float(rating),
                'comment': comment
            }
        )
        message = 'Review Anda berhasil diperbarui!' if not created else 'Terima kasih atas review Anda!'

        return JsonResponse({
            'status': 'success',
            'message': message,
            'review': {
                'user': review.user.username,
                'rating': review.rating,
                'comment': review.comment,
            }
        })
    except Venue.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Venue tidak ditemukan.'}, status=404)
    except ValueError:
        return JsonResponse({'status': 'error', 'message': 'Rating tidak valid.'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Terjadi kesalahan: {str(e)}'}, status=500)

def edit_review(request):
    return

def delete_review(request):
    return


def get_venue_reviews(request, venue_id):
    venue = get_object_or_404(Venue, pk=venue_id)
    reviews_qs = venue.reviews.all().order_by('-created_at')

    reviews_data = []
    for review in reviews_qs:
        reviews_data.append({
            'id': review.id,
            'user_name': review.user.get_full_name() or review.user.username, # Get full name or username
            'rating': review.rating,
            'comment': review.comment,
            'created_at': review.created_at.isoformat()
        })

    return JsonResponse(reviews_data, safe=False)