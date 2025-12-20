from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

class FAQ(models.Model):
    CATEGORY_CHOICES = [
        ('umum', 'Umum'),
        ('booking', 'Booking'),
        ('pembayaran', 'Pembayaran'),
        ('venue', 'Venue'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.CharField(max_length=255)
    answer = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question

    class Meta:
        ordering = ['-created_at']
    