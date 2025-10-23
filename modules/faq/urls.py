from django.urls import path
from . import views

app_name = 'faq'

urlpatterns = [
    path('', views.faq_list, name='faq_list'),
    path('add/', views.add_faq, name='add_faq'),
    path('edit/<int:faq_id>/', views.edit_faq, name='edit_faq'),
    path('delete/<int:faq_id>/', views.delete_faq, name='delete_faq'),
    path('filter/', views.filter_faq, name='filter_faq'),
]