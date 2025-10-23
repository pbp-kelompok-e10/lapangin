from django.db import models
from django.contrib.auth.models import User

class Venue(models.Model):
    name = models.CharField(max_length=255)  # Stadium
    city = models.CharField(max_length=100)  # City
    home_teams = models.TextField(blank=True)  # HomeTeams
    capacity = models.IntegerField()  # Capacity
    country = models.CharField(max_length=100)  # Country
    price = models.DecimalField(max_digits=10, decimal_places=2)
    thumbnail = models.TextField(default='https://via.placeholder.com/300x200', blank=True)  # For Google image URLs
    description = models.TextField(default='', blank=True)


    def __str__(self):
        return self.name