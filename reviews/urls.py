from django.urls import path
from . import views

urlpatterns = [
    path("", views.review_list, name="review_list"),
    path("leave/<int:contract_id>/", views.leave_review, name="leave_review"),
    path("profile/<str:username>/", views.user_reviews, name="user_reviews"),
]
