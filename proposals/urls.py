from django.urls import path
from . import views

urlpatterns = [
    path("", views.proposal_list, name="proposal_list"),
    path("<int:proposal_id>/", views.proposal_detail, name="proposal_detail"),
    path("<int:proposal_id>/accept/", views.accept_proposal, name="accept_proposal"),
    path("<int:proposal_id>/reject/", views.reject_proposal, name="reject_proposal"),
    path("<int:proposal_id>/counter/", views.counter_proposal, name="counter_proposal"),
    path("dashboard/list/", views.dashboard_proposals, name="dashboard_proposals"),
]
