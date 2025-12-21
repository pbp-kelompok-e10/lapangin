from django.urls import path
from modules.main.views import *
from django.conf import settings
from django.conf.urls.static import static
from modules.accounts.views import login_user, register, logout_user, get_page_data, profile_page

app_name = 'accounts'

urlpatterns = [
    path('login/', login_user, name='login'),
    path('register/', register, name='register'),
    path('logout/', logout_user, name='logout'),
    path('page-data', get_page_data, name='get_page_data'),
    path('profile/', profile_page, name='profile' )
]
