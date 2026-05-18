from django.urls import path
from . import views

urlpatterns = [
    path('', views.messages_page, name='messages'),
    path('<int:thread_id>/', views.thread_view, name='messages_thread'),
    path('<int:thread_id>/send/', views.send_message, name='messages_send'),
    path('<int:thread_id>/read/', views.mark_read, name='messages_read'),
    path('start/<int:user_id>/', views.start_thread, name='messages_start'),
    path('<int:thread_id>/poll/', views.poll_thread, name='messages_poll'),
]
