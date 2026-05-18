from django.urls import path
from . import views

urlpatterns = [
    path('', views.browse, name='browse'),
    path('find/', views.jobs_list, name='jobs_list'),
    path('search/', views.search_results, name='search_results'),
    path('category/<slug:slug>/', views.category_view, name='category_view'),
    path('post/', views.post_job, name='post_job'),
    path('<int:job_id>/propose/', views.propose_to_job, name='propose_to_job'),
    path('<int:job_id>/', views.job_detail, name='job_detail'),
    path('dashboard/list/', views.client_jobs, name='client_jobs'),
]
