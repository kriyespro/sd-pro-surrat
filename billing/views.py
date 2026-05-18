from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .models import Plan, Subscription


@login_required
def pricing_page(request):
    plans = Plan.objects.filter(is_active=True).order_by("price_monthly")
    return render(request, 'pages/pricing.jinja', {'plans': plans})


@login_required
def checkout(request):
    plan_id = request.POST.get("plan_id")
    cycle = request.POST.get("cycle", "monthly")
    plan = get_object_or_404(Plan, id=plan_id) if plan_id else Plan.objects.order_by("price_monthly").first()
    if not plan:
        plan = Plan.objects.create(
            name="Free",
            price_monthly=0,
            price_yearly=0,
            max_jobs_per_month=5,
            commission_rate=15,
            boosted_proposals=0,
            is_featured=False,
        )
    Subscription.objects.update_or_create(
        user=request.user,
        defaults={
            "plan": plan,
            "billing_cycle": cycle,
            "status": "active",
            "current_period_end": timezone.now() + timezone.timedelta(days=30 if cycle == "monthly" else 365),
        },
    )
    return redirect("billing_manage")


@login_required
def billing_manage(request):
    subscription = Subscription.objects.filter(user=request.user).select_related("plan").first()
    if not subscription:
        return HttpResponse("<div class='text-sm text-[var(--text-muted)]'>No active subscription</div>")
    return HttpResponse(
        f"<div class='text-sm text-[var(--text-muted)]'>Plan: {subscription.plan} | "
        f"Cycle: {subscription.billing_cycle} | Status: {subscription.status}</div>"
    )

