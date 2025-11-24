from django.db import models
from ..venue.models import Venue;
from django.contrib.auth.models import User

class Review(models.Model):
    venue = models.ForeignKey('venue.Venue', on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.venue.name} by {self.user.username}"