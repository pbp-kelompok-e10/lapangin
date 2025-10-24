from django.urls import path
from modules.main.views import *
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'venue'

from modules.venue.views import venue_detail, get_venue_detail_api, search_venue

urlpatterns = [
    path('', search_venue, name='search_venue'),
    path('venue/<int:venue_id>/', venue_detail, name='venue_detail'),
    path('edit/<int:venue_id>/', views.edit_venue, name='edit_venue'),
    path('delete/<int:venue_id>/', views.delete_venue, name='delete_venue'),
    path('create/', views.create_venue, name='create_venue'),
    path('api/search/', views.search_venues_api, name='search_venues_api'),
    path('api/detail/<int:venue_id>/', get_venue_detail_api, name='get_venue_detail_api'),
]
