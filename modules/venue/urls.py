from django.urls import path
from modules.main.views import *
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'venue'

from modules.venue.views import search_venue, venue_detail

urlpatterns = [
    path('', search_venue, name='search_venue'),
    path('venue/<int:venue_id>/', venue_detail, name='venue_detail'),
    path('edit/<int:venue_id>/', views.edit_venue, name='edit_venue'),
    path('delete/<int:venue_id>/', views.delete_venue, name='delete_venue'),
    path('create/', views.create_venue, name='create_venue'),
    path('api/search/', views.search_venues_api, name='search_venues_api'),
    # path('import/', views.import_venues, name='import_venues'),

]
