from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.validators import MinValueValidator
import uuid

class User(AbstractUser):
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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    home_teams = models.TextField(blank=True)
    capacity = models.IntegerField()
    country = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.0)])
    thumbnail = models.TextField(default='', blank=True)
    description = models.TextField(default='', blank=True)
    facilities = models.TextField(default='', blank=True)
    rules = models.TextField(default='', blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    
    def __str__(self):
        return self.name