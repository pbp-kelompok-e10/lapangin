from django.urls import path
from modules.main.views import *
from django.conf import settings
from django.conf.urls.static import static

app_name = 'main'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('about', show_about, name='about')
]
