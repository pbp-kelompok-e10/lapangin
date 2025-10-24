from django.urls import path
from modules.review.views import *
from django.conf import settings
from django.conf.urls.static import static

app_name = 'review'

urlpatterns = [
    path('add/', add_review, name='add_review'),
    path('delete/<int:review_id>', delete_review, name='delete_review'),
    path('edit/<int:review_id>', edit_review, name="edit_review"),
    path('reviews/<int:venue_id>', get_venue_reviews, name = "get_venue_reviews")
]
