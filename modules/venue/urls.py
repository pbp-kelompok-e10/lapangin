from django.urls import path
from modules.main.views import *
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'venue'

from modules.venue.views import delete_venue_api,edit_venue_flutter,create_venue_flutter,venue_detail, get_venue_detail_api, search_venue, get_recommended_venues_api, show_json, get_venues_api, check_venue_creation_permission_api

urlpatterns = [
    path('', search_venue, name='search_venue'),
    path('json/',show_json, name='show_json'),
    path('detail/<uuid:venue_id>/', venue_detail, name='venue_detail'),
    path('edit/<uuid:venue_id>/', views.edit_venue, name='edit_venue'),
    path('delete/<uuid:venue_id>/', views.delete_venue, name='delete_venue'),
    path('create/', views.create_venue, name='create_venue'),
    path('api/search/', views.search_venues_api, name='search_venues_api'),
    path('api/detail/<uuid:venue_id>/', get_venue_detail_api, name='get_venue_detail_api'),
    path('api/recommended', get_recommended_venues_api, name='recommended_venue'),
    path('api/venues', get_venues_api, name='get_venues_api'),
    path('api/permission/create/', check_venue_creation_permission_api, name='check_create_permission_api'),
    path('api/create/', create_venue_flutter, name="create_venue_api"),
    path('api/edit/<uuid:venue_id>', edit_venue_flutter, name="edit_venue_api"),
    path('api/delete/<uuid:venue_id>/', delete_venue_api, name="delete_venue_api")
]
