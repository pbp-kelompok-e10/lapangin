from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class User(AbstractUser):  # Jika belum extend, tambahkan ini
    is_venue_provider = models.BooleanField(default=False)
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='venue_user_set',
        blank=True,
        help_text=('The groups this user belongs to.'),
        related_query_name="venue_user",
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='venue_user_permissions_set',
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='venue_user',
    )

class Venue(models.Model):
    name = models.CharField(max_length=255)  # Stadium
    city = models.CharField(max_length=100)  # City
    home_teams = models.TextField(blank=True)  # HomeTeams
    capacity = models.IntegerField()  # Capacity
    country = models.CharField(max_length=100)  # Country
    price = models.DecimalField(max_digits=10, decimal_places=2)
    thumbnail = models.TextField(default='https://via.placeholder.com/300x200', blank=True)  # For Google image URLs
    description = models.TextField(default='', blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)  # Tambahkan ini
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    
    def __str__(self):
        return self.name