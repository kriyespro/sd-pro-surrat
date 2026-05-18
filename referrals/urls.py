from django.urls import path
from . import views

urlpatterns = [
    path('', views.referral_page, name='referral'),
    path('stats/', views.referral_stats, name='referral_stats'),
    path('payout/', views.payout_request, name='referral_payout'),
]
