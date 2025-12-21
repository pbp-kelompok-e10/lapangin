from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [
    # ========== WEB VIEWS (Return HTML) ==========
    path('list/', views.user_list, name='user_list'),
    path('detail/<int:user_id>/', views.user_detail, name='user_detail'),
    path('create/', views.user_create, name='user_create'),
    path('edit/<int:user_id>/', views.user_edit, name='user_edit'),
    path('delete/<int:user_id>/', views.user_delete, name='user_delete'),
    path('toggle-status/<int:user_id>/', views.user_toggle_status, name='user_toggle_status'),
    
    # ========== API VIEWS (Return JSON for Flutter) ==========
    path('api/list/', views.user_list_api, name='user_list_api'),
    
    # Profile API (GET current user's profile & UPDATE current user's profile)
    path('api/profile/', views.get_profile, name='get_profile'),
    path('api/update-profile/', views.update_profile, name='update_profile'),
]