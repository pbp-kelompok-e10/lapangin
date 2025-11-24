from django.db import models
from django.conf import settings
from modules.venue.models import Venue

class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    venue = models.ForeignKey('venue.Venue', on_delete=models.CASCADE, related_name='bookings')
    booking_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.venue.name} by {self.user.username} on {self.booking_date}"

    class Meta:
        ordering = ['-booking_date']
        unique_together = ('venue', 'booking_date')