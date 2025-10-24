from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg
from .models import Review
from modules.venue.models import Venue
from decimal import Decimal, ROUND_HALF_UP  # <-- IMPORT INI

@receiver([post_save, post_delete], sender=Review)
def update_venue_rating(sender, instance, **kwargs):
    venue = instance.venue

    new_rating = Review.objects.filter(venue=venue).aggregate(
        avg_rating=Avg('rating')
    )['avg_rating']

    if new_rating is not None:
        venue.rating = Decimal(new_rating).quantize(
            Decimal('0.1'),
            rounding=ROUND_HALF_UP
        )
    else:
        venue.rating = Decimal('0.0')
    venue.save(update_fields=['rating'])