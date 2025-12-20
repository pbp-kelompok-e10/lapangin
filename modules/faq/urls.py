from django.urls import path
from . import views

app_name = 'faq'

urlpatterns = [
    # Web URLs
    path('', views.faq_list, name='faq_list'),
    path('add/', views.add_faq, name='add_faq'),
    path('edit/<uuid:faq_id>/', views.edit_faq, name='edit_faq'), 
    path('delete/<uuid:faq_id>/', views.delete_faq, name='delete_faq'),  
    path('filter/', views.filter_faq, name='filter_faq'),
    
    # Flutter API
    path('json/', views.show_json, name='show_json'),
    path('json/<str:category>/', views.show_json_by_category, name='show_json_by_category'),
    path('create-flutter/', views.create_faq_flutter, name='create_faq_flutter'),
    path('delete-flutter/<uuid:faq_id>/', views.delete_faq_flutter, name='delete_faq_flutter'),  
    path('update-flutter/<uuid:faq_id>/', views.update_faq_flutter, name='update_faq_flutter'),  
]