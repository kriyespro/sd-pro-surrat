from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import json

from .models import PayoutRequest, Referral


@login_required
def referral_page(request):
    referrals = Referral.objects.filter(referrer=request.user)
    payouts = PayoutRequest.objects.filter(user=request.user).order_by('-created_at')[:10]
    referrals_data = [
        {
            "name": r.referred.get_full_name() or r.referred.username,
            "initials": r.referred.initials,
            "color": "linear-gradient(135deg,#0D6E6E,#E8A830)",
            "type": r.referred.role.title(),
            "date": r.created_at.strftime("%b %d"),
            "earned": "₹700" if r.first_job_bonus_paid else ("₹500" if r.signup_bonus_paid else "₹0"),
            "status": "Active" if r.signup_bonus_paid else "Pending",
        }
        for r in referrals
    ]
    total_earned = sum(700 if r.first_job_bonus_paid else (500 if r.signup_bonus_paid else 0) for r in referrals)
    pending = sum(float(p.amount) for p in payouts if p.status == "pending")
    return render(
        request,
        "pages/referral.jinja",
        {
            "referrals_json": json.dumps(referrals_data),
            "total_earned": int(total_earned),
            "pending_amount": int(pending),
            "total_referrals": referrals.count(),
        },
    )


@login_required
def referral_stats(request):
    referrals = Referral.objects.filter(referrer=request.user)
    total_earned = sum(700 if r.first_job_bonus_paid else (500 if r.signup_bonus_paid else 0) for r in referrals)
    return HttpResponse(
        f"<div class='text-sm text-[var(--text-muted)]'>Referrals: {referrals.count()} | Earned: ₹{int(total_earned)}</div>"
    )


@login_required
def payout_request(request):
    amount = request.POST.get("amount") or 500
    upi_id = request.POST.get("upi_id") or f"{request.user.username}@upi"
    PayoutRequest.objects.create(user=request.user, amount=amount, status="pending", upi_id=upi_id)
    return HttpResponse("<div class='sp-badge sp-badge-gold'>Payout request submitted</div>")

