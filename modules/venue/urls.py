from django.urls import path
from modules.main.views import *
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'search_venue'

urlpatterns = [
    path('', views.search_venue, name='search_venue'),
]
