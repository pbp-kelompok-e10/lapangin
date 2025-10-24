# modules/booking/urls.py
from django.urls import path
from . import views

app_name = 'booking'

urlpatterns = [
    path('api/get_booked/<int:venue_id>/', views.get_booked_dates_api, name='get_booked_dates_api'),
    path('api/create/', views.create_booking_api, name='create_booking_api'),
]