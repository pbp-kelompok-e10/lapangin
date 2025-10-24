from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg
from .models import Review
from modules.venue.models import Venue

@receiver([post_save, post_delete], sender=Review)
def update_venue_rating(sender, instance, **kwargs):
    venue = instance.venue

    new_rating = Review.objects.filter(venue=venue).aggregate(
        avg_rating=Avg('rating')
    )['avg_rating']

    if new_rating is not None:
        venue.rating = round(new_rating, 1)
    else:
        venue.rating = 0

    venue.save(update_fields=['rating'])