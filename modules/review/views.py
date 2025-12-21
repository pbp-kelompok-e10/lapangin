from django.shortcuts import render
from .models import Review
from ..venue.models import Venue
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import ReviewForm
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

def is_admin(user):
    return user.is_staff or user.is_superuser

@csrf_exempt
@login_required
@require_POST
def add_review(request):
    try:
        venue_id = request.POST.get('venue_id')
        if not venue_id:
            return JsonResponse({'status': 'error', 'message': 'Venue ID diperlukan.'}, status=400)

        venue = Venue.objects.get(pk=venue_id)

        form = ReviewForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data

            review, created = Review.objects.update_or_create(
                user=request.user,
                venue=venue,
                defaults={
                    'rating': data['rating'],
                    'comment': data['comment']
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
        
        else:
            return JsonResponse({'status': 'error', 'message': 'Data tidak valid.', 'errors': form.errors.as_json()}, status=400)

    except Venue.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Venue tidak ditemukan.'}, status=404)
    except (ValueError, TypeError):
        return JsonResponse({'status': 'error', 'message': 'Venue ID tidak valid.'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Terjadi kesalahan: {str(e)}'}, status=500)


@login_required
@require_http_methods(["GET", "POST"])
def edit_review(request, review_id):
    try:
        review = Review.objects.get(pk=review_id)

        if not (review.user == request.user or request.user.is_superuser or request.user.is_staff):
            return JsonResponse({'success': False, 'message': 'Anda tidak punya izin untuk mengedit review ini.'}, status=403)

        if request.method == 'POST':
            form = ReviewForm(request.POST, instance=review)
            if form.is_valid():
                form.save()
                updated_review_data = {
                    'id': review.id,
                    'user_name': review.user.get_full_name() or review.user.username,
                    'user_id': review.user.id,
                    'rating': review.rating,
                    'comment': review.comment,
                    'created_at': review.created_at.isoformat()
                }
                return JsonResponse({
                    'success': True,
                    'message': 'Review berhasil diperbarui.',
                    'review': updated_review_data
                })
            else:
                return JsonResponse({'success': False, 'message': 'Data tidak valid.', 'errors': form.errors.as_json()}, status=400)
        
        else:
            review_data = {
                'rating': review.rating,
                'comment': review.comment,
            }
            return JsonResponse({'success': True, 'data': review_data})

    except Review.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Data review tidak ditemukan.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Terjadi kesalahan: {str(e)}'}, status=500)

@login_required
@require_POST
def delete_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id)

    if not (review.user == request.user or request.user.is_superuser or request.user.is_staff):
        return JsonResponse({'status': 'error', 'message': 'Anda tidak punya izin untuk menghapus review ini.'}, status=403)

    try:
        review_id_deleted = review.id
        review.delete()
        return JsonResponse({'status': 'success', 'message': 'Review berhasil dihapus.', 'deleted_review_id': review_id_deleted})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Terjadi kesalahan saat menghapus: {str(e)}'}, status=500)

def get_venue_reviews(request, venue_id):
    venue = Venue.objects.get(pk=venue_id)
    reviews_qs = venue.reviews.select_related('user').all().order_by('-created_at')

    current_user_id = request.user.id if request.user.is_authenticated else None

    reviews_data = []
    for review in reviews_qs:
        reviews_data.append({
            'id': review.id,
            'user_name': review.user.get_full_name() or review.user.username,
            'user_id': review.user.id,
            'rating': review.rating,
            'comment': review.comment,
            'created_at': review.created_at.isoformat()
        })

    return JsonResponse({
        'reviews': reviews_data,
        'current_user_id': current_user_id
    })