from django.urls import path
from modules.main.views import *
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'venue'

from modules.venue.views import search_venue

urlpatterns = [
    path('', search_venue, name='search_venue'),
    path('venue/<int:venue_id>/', views.venue_detail, name='venue_detail'),
]
