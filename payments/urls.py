from django.urls import path
from . import views

urlpatterns = [
    path('', views.payments_page, name='payments'),
    path('add/', views.add_funds, name='payments_add'),
    path('callback/', views.razorpay_callback, name='payments_callback'),
    path('release/<int:milestone_id>/', views.release_funds, name='payments_release'),
    path('transactions/', views.transaction_list, name='payments_transactions'),
    path('dispute/<int:contract_id>/', views.dispute_contract, name='payments_dispute'),
]
