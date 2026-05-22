from django.urls import path
from . import views
from reviews.views import user_reviews

urlpatterns = [
    path('', views.home, name='home'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/register/', views.register_view, name='register'),
    path('auth/logout/', views.logout_view, name='logout'),
    path('auth/google/', views.google_login_start, name='google_login_start'),
    path('auth/google/callback/', views.google_callback, name='google_callback'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('profile/<str:username>/reviews/', user_reviews, name='profile_reviews'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/profile/edit/', views.profile_edit, name='profile_edit'),
    path('onboarding/', views.onboarding, name='onboarding'),
]
