from django.urls import path
from . import views

urlpatterns = [
    path('pricing/', views.pricing_page, name='pricing'),
    path('billing/checkout/', views.checkout, name='billing_checkout'),
    path('billing/manage/', views.billing_manage, name='billing_manage'),
]
