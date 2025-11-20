# modules/booking/urls.py
from django.urls import path
from . import views

app_name = 'booking'

urlpatterns = [
    path('api/get_booked/<uuid:venue_id>/', views.get_booked_dates_api, name='get_booked_dates_api'),
    path('api/create/', views.create_booking_api, name='create_booking_api'),
    path('history/', views.booking_history_page, name='booking_history_page'),
    path('api/history/', views.get_user_bookings_api, name='get_user_bookings_api'),
    path('api/edit/<int:booking_id>/', views.edit_booking_api, name='edit_booking_api'),
    path('api/delete/<int:booking_id>/', views.delete_booking_api, name='delete_booking_api'),
]