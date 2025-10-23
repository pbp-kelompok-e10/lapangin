from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [
    path('list/', views.user_list, name='user_list'),
    path('detail/<int:user_id>/', views.user_detail, name='user_detail'),
    path('create/', views.user_create, name='user_create'),
    path('edit/<int:user_id>/', views.user_edit, name='user_edit'),
    path('delete/<int:user_id>/', views.user_delete, name='user_delete'),
    path('toggle-status/<int:user_id>/', views.user_toggle_status, name='user_toggle_status'),
]