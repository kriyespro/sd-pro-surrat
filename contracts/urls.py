from django.urls import path
from . import views

urlpatterns = [
    path("", views.contract_list, name="contract_list"),
    path("<int:contract_id>/", views.contract_detail, name="contract_detail"),
    path("<int:contract_id>/sign/", views.sign_contract, name="sign_contract"),
    path("<int:contract_id>/milestones/add/", views.add_milestone, name="add_milestone"),
    path("milestones/<int:milestone_id>/submit/", views.submit_milestone, name="submit_milestone"),
    path("milestones/<int:milestone_id>/approve/", views.approve_milestone, name="approve_milestone"),
    path("milestones/<int:milestone_id>/revision/", views.revision_request, name="revision_request"),
]
