from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required

from .models import Contract, Milestone, RevisionRequest


@login_required
def contract_list(request):
    contracts = Contract.objects.filter(client=request.user) | Contract.objects.filter(freelancer=request.user)
    return render(request, "pages/contract.jinja", {"contracts": contracts.distinct()})


@login_required
def contract_detail(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id)
    return render(request, "pages/contract.jinja", {"contracts": [contract]})


@login_required
def sign_contract(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id)
    if request.user == contract.client:
        contract.signed_by_client = True
    if request.user == contract.freelancer:
        contract.signed_by_freelancer = True
    contract.save(update_fields=["signed_by_client", "signed_by_freelancer"])
    return HttpResponse("<div class='sp-badge sp-badge-green'>Contract signed</div>")


@login_required
def add_milestone(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id)
    if request.user != contract.client:
        return HttpResponseForbidden("Only the client can add milestones.")
    if request.method != "POST":
        return HttpResponse("Method not allowed", status=405)
    title = (request.POST.get("title") or "").strip()
    amount = request.POST.get("amount") or 0
    due_date = request.POST.get("due_date") or None
    description = (request.POST.get("description") or "").strip()
    if not title:
        return HttpResponse("<div class='sp-badge sp-badge-red'>Title required</div>", status=400)
    order = contract.milestones.count() + 1
    m = Milestone.objects.create(
        contract=contract,
        title=title,
        amount=amount,
        due_date=due_date,
        description=description,
        order=order,
    )
    return HttpResponse(f"""
<div class="ms-card" id="ms-{m.id}">
  <div class="ms-head">
    <span class="ms-title">{m.title}</span>
    <span class="sp-badge sp-badge-gold">Pending</span>
  </div>
  <div class="ms-meta">₹{m.amount} · Due {m.due_date or 'TBD'}</div>
  {f'<p class="ms-desc">{m.description}</p>' if m.description else ''}
  <div class="ms-actions" id="ms-actions-{m.id}">
    <form hx-post="/contracts/milestones/{m.id}/submit/" hx-target="#ms-actions-{m.id}" hx-swap="innerHTML" style="display:inline">
      <input type="hidden" name="csrfmiddlewaretoken" value="">
      <button type="submit" class="btn-sm" style="background:var(--gold);color:var(--dark);border:none">Submit deliverable</button>
    </form>
  </div>
</div>
""")


@login_required
def submit_milestone(request, milestone_id):
    milestone = get_object_or_404(Milestone, id=milestone_id)
    milestone.status = "submitted"
    milestone.save(update_fields=["status"])
    return HttpResponse("<div class='sp-badge sp-badge-gold'>Deliverable submitted</div>")


@login_required
def approve_milestone(request, milestone_id):
    milestone = get_object_or_404(Milestone, id=milestone_id)
    milestone.status = "approved"
    milestone.save(update_fields=["status"])
    return HttpResponse("<div class='sp-badge sp-badge-green'>Milestone approved</div>")


@login_required
def revision_request(request, milestone_id):
    milestone = get_object_or_404(Milestone, id=milestone_id)
    RevisionRequest.objects.create(
        milestone=milestone,
        requested_by=request.user,
        note=request.POST.get("note", "Please make revisions."),
    )
    return HttpResponse("<div class='sp-badge sp-badge-red'>Revision requested</div>")
