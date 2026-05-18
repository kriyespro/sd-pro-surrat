from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required

from contracts.models import Contract
from .models import Proposal


def _proposal_for_job_owner(request, proposal_id):
    proposal = get_object_or_404(
        Proposal.objects.select_related("job"), id=proposal_id
    )
    if proposal.job.client_id != request.user.pk:
        return None
    return proposal


@login_required
def proposal_list(request):
    if request.user.is_freelancer:
        proposals = Proposal.objects.filter(freelancer=request.user).select_related("job")
    else:
        proposals = Proposal.objects.filter(job__client=request.user).select_related("job", "freelancer")
    return render(request, "partials/_proposal_card.jinja", {"proposals": proposals})


@login_required
def proposal_detail(request, proposal_id):
    proposal = get_object_or_404(Proposal, id=proposal_id)
    if request.user.is_freelancer:
        if proposal.freelancer_id != request.user.pk:
            return HttpResponseForbidden(
                "You can only view proposals you submitted."
            )
    elif request.user.is_client:
        if proposal.job.client_id != request.user.pk:
            return HttpResponseForbidden(
                "You can only view proposals on jobs you posted."
            )
    else:
        return HttpResponseForbidden("Invalid account role.")
    return render(request, "partials/_proposal_card.jinja", {"proposals": [proposal]})


@login_required
def dashboard_proposals(request):
    if request.user.is_freelancer:
        proposals = Proposal.objects.filter(freelancer=request.user).select_related("job", "job__client")
    else:
        proposals = Proposal.objects.filter(job__client=request.user).select_related("job", "freelancer")
    return render(request, "partials/_proposal_card.jinja", {"proposals": proposals})


@login_required
def accept_proposal(request, proposal_id):
    proposal = _proposal_for_job_owner(request, proposal_id)
    if proposal is None:
        return HttpResponseForbidden(
            "Only the client who posted this job can accept proposals."
        )
    proposal.status = "accepted"
    proposal.save(update_fields=["status"])

    # Create contract if one doesn't already exist for this proposal
    Contract.objects.get_or_create(
        proposal=proposal,
        defaults={
            "job": proposal.job,
            "client": proposal.job.client,
            "freelancer": proposal.freelancer,
            "total_value": proposal.proposed_rate,
            "status": "active",
            "signed_by_client": True,
        },
    )

    return HttpResponse("<div class='sp-badge sp-badge-green'>Proposal accepted</div>")


@login_required
def reject_proposal(request, proposal_id):
    proposal = _proposal_for_job_owner(request, proposal_id)
    if proposal is None:
        return HttpResponseForbidden(
            "Only the client who posted this job can reject proposals."
        )
    proposal.status = "rejected"
    proposal.save(update_fields=["status"])
    return HttpResponse("<div class='sp-badge sp-badge-red'>Proposal rejected</div>")


@login_required
def counter_proposal(request, proposal_id):
    proposal = _proposal_for_job_owner(request, proposal_id)
    if proposal is None:
        return HttpResponseForbidden(
            "Only the client who posted this job can send a counter offer."
        )
    Proposal.objects.create(
        job=proposal.job,
        freelancer=proposal.freelancer,
        cover_letter=request.POST.get("cover_letter", "Counter offer"),
        proposed_rate=request.POST.get("proposed_rate") or proposal.proposed_rate,
        delivery_days=request.POST.get("delivery_days") or proposal.delivery_days,
        status="pending",
        is_counter=True,
        parent=proposal,
    )
    return HttpResponse("<div class='sp-badge sp-badge-gold'>Counter offer sent</div>")
