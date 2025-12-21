# modules/booking/urls.py
from django.urls import path
from . import views

app_name = 'booking'

urlpatterns = [
    # Web API endpoints
    path('api/get_booked/<uuid:venue_id>/', views.get_booked_dates_api, name='get_booked_dates_api'),
    path('api/create/', views.create_booking_api, name='create_booking_api'),
    path('history/', views.booking_history_page, name='booking_history_page'),
    path('api/history/', views.get_user_bookings_api, name='get_user_bookings_api'),
    path('api/edit/<int:booking_id>/', views.edit_booking_api, name='edit_booking_api'),
    path('api/delete/<int:booking_id>/', views.delete_booking_api, name='delete_booking_api'),
    
    # Flutter API endpoints
    path('flutter/booked-dates/<uuid:venue_id>/', views.flutter_get_booked_dates, name='flutter_get_booked_dates'),
    path('flutter/create/', views.flutter_create_booking, name='flutter_create_booking'),
    path('flutter/my-bookings/', views.flutter_get_user_bookings, name='flutter_get_user_bookings'),
    path('flutter/edit/<int:booking_id>/', views.flutter_edit_booking, name='flutter_edit_booking'),
    path('flutter/delete/<int:booking_id>/', views.flutter_delete_booking, name='flutter_delete_booking'),
]