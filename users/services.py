"""Dashboard and user-facing aggregates."""

from django.db.models import Count, Q

from billing.models import Subscription
from contracts.models import Contract
from jobs.models import Job
from proposals.models import Proposal


def subscription_plan_label(user):
    try:
        sub = Subscription.objects.select_related("plan").get(user=user)
        if sub.status == "active" and sub.plan:
            return sub.plan.name
    except Subscription.DoesNotExist:
        pass
    return "Free"


def build_dashboard_context(user):
    """Role-specific lists and stats for the main dashboard."""
    ctx = {
        "subscription_plan_label": subscription_plan_label(user),
    }
    if user.is_client:
        jobs_qs = (
            Job.objects.filter(client=user)
            .select_related("category")
            .annotate(proposal_count=Count("proposals", distinct=True))
            .order_by("-created_at")
        )
        proposals_qs = Proposal.objects.filter(job__client=user).select_related(
            "job", "freelancer"
        ).order_by("-created_at")
        contracts_qs = (
            Contract.objects.filter(client=user)
            .select_related("job", "freelancer")
            .prefetch_related("milestones")
            .order_by("-created_at")
        )
        agg = jobs_qs.aggregate(
            active_jobs=Count("id", filter=Q(status="active")),
            total_jobs=Count("id"),
        )
        ctx.update(
            {
                "dash_jobs": list(jobs_qs[:100]),
                "dash_proposals": list(proposals_qs[:100]),
                "dash_contracts": list(contracts_qs[:50]),
                "dash_stats": {
                    "active_jobs": agg["active_jobs"] or 0,
                    "total_jobs": agg["total_jobs"] or 0,
                    "pending_proposals": proposals_qs.filter(status="pending").count(),
                    "active_contracts": contracts_qs.filter(status="active").count(),
                },
            }
        )
    else:
        proposals_qs = Proposal.objects.filter(freelancer=user).select_related(
            "job", "job__client"
        ).order_by("-created_at")
        contracts_qs = (
            Contract.objects.filter(freelancer=user)
            .select_related("job", "client")
            .prefetch_related("milestones")
            .order_by("-created_at")
        )
        ctx.update(
            {
                "dash_jobs": [],
                "dash_proposals": list(proposals_qs[:100]),
                "dash_contracts": list(contracts_qs[:50]),
                "dash_stats": {
                    "pending_bids": proposals_qs.filter(status="pending").count(),
                    "shortlisted": proposals_qs.filter(status="shortlisted").count(),
                    "active_contracts": contracts_qs.filter(status="active").count(),
                    "accepted": proposals_qs.filter(status="accepted").count(),
                },
            }
        )
    return ctx


def resolve_dashboard_page(user, raw_page):
    """Validate tab query param per role."""
    if user.is_client:
        allowed = {"overview", "jobs", "proposals", "contracts"}
    else:
        allowed = {"overview", "proposals", "contracts"}
    if raw_page in allowed:
        return raw_page
    return "overview"
