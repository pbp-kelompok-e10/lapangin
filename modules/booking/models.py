from django.db import models
from django.conf import settings
from modules.venue.models import Venue

class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='bookings')
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.venue.name} by {self.user.username} [{self.start_date} - {self.end_date}]"

    class Meta:
        ordering = ['start_date']