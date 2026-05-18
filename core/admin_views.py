from functools import wraps

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from billing.models import Subscription
from contracts.models import Contract
from jobs.models import Job
from payments.models import Dispute, Transaction
from proposals.models import Proposal
from reviews.models import Review
from users.models import User


def superuser_required(fn):
    @wraps(fn)
    @login_required
    def inner(request, *args, **kwargs):
        if not request.user.is_superuser:
            return HttpResponseForbidden("Superuser access required.")
        return fn(request, *args, **kwargs)
    return inner


def _base_ctx(now):
    today = now.date()
    week_ago = now - timezone.timedelta(days=7)
    month_ago = now - timezone.timedelta(days=30)

    release_qs = Transaction.objects.filter(type="release", status="success")
    daily_rev = []
    for i in range(6, -1, -1):
        d = today - timezone.timedelta(days=i)
        amt = release_qs.filter(created_at__date=d).aggregate(t=Sum("amount"))["t"] or 0
        daily_rev.append({"day": d.strftime("%d %b"), "amt": float(amt)})

    return {
        "revenue_today": release_qs.filter(created_at__date=today).aggregate(t=Sum("amount"))["t"] or 0,
        "revenue_week":  release_qs.filter(created_at__gte=week_ago).aggregate(t=Sum("amount"))["t"] or 0,
        "revenue_month": release_qs.filter(created_at__gte=month_ago).aggregate(t=Sum("amount"))["t"] or 0,
        "daily_rev": daily_rev,
        "total_users":     User.objects.count(),
        "new_users_week":  User.objects.filter(date_joined__gte=week_ago).count(),
        "active_users":    User.objects.filter(last_login__gte=month_ago).count(),
        "freelancers":     User.objects.filter(role="freelancer").count(),
        "clients":         User.objects.filter(role="client").count(),
        "jobs_posted":     Job.objects.count(),
        "jobs_active":     Job.objects.filter(status="active").count(),
        "jobs_completed":  Job.objects.filter(status="completed").count(),
        "contracts_active":    Contract.objects.filter(status="active").count(),
        "contracts_completed": Contract.objects.filter(status="completed").count(),
        "contracts_disputed":  Contract.objects.filter(status="disputed").count(),
        "active_subscriptions":   Subscription.objects.filter(status="active").count(),
        "pending_reviews_count":  Review.objects.filter(is_approved=False).count(),
        "open_disputes":          Dispute.objects.filter(status__in=["open", "in_review"]).count(),
        "now": now,
    }


@superuser_required
def mission_control(request):
    now = timezone.now()
    today = now.date()
    week_ago = now - timezone.timedelta(days=7)
    ctx = _base_ctx(now)

    # ── Moderation queues
    ctx["moderation_reviews"]  = Review.objects.filter(is_approved=False).select_related("reviewer", "reviewee").order_by("-created_at")[:20]
    ctx["open_dispute_list"]   = Dispute.objects.filter(status__in=["open", "in_review"]).select_related("contract", "raised_by").order_by("-created_at")[:20]
    ctx["pending_jobs"]        = Job.objects.filter(status="draft").select_related("client").order_by("-created_at")[:20]
    ctx["unverified_users"]    = User.objects.filter(is_verified=False, is_staff=False, is_active=True).order_by("-date_joined")[:20]

    # ── Leaderboards
    top_fl_qs = (
        User.objects.filter(role="freelancer")
        .annotate(completed_contracts=Count("freelancer_contracts", filter=Q(freelancer_contracts__status="completed")))
        .order_by("-completed_contracts", "-date_joined")[:8]
    )
    top_freelancers = []
    for u in top_fl_qs:
        try:
            u._profile = u.freelancer_profile
        except Exception:
            u._profile = None
        top_freelancers.append(u)
    ctx["top_freelancers"] = top_freelancers
    ctx["top_clients"] = (
        User.objects.filter(role="client")
        .annotate(total_contracts=Count("client_contracts"))
        .order_by("-total_contracts", "-date_joined")[:8]
    )

    # ── Live feed
    ctx["recent_signups"]      = User.objects.order_by("-date_joined")[:15]
    ctx["recent_transactions"] = Transaction.objects.select_related("wallet__user").order_by("-created_at")[:15]

    # ── Management tables
    raw_users = list(
        User.objects.order_by("-date_joined")
        .annotate(
            n_jobs=Count("jobs", distinct=True),
            n_contracts=Count("client_contracts", distinct=True) + Count("freelancer_contracts", distinct=True),
        )
        .prefetch_related("subscription")[:300]
    )
    from billing.models import Subscription as Sub
    sub_map = {s.user_id: s for s in Sub.objects.filter(status="active").select_related("plan")}
    for u in raw_users:
        u._sub = sub_map.get(u.id)
    ctx["all_users"] = raw_users
    ctx["all_jobs"] = (
        Job.objects.select_related("client", "category")
        .annotate(proposal_count=Count("proposals", distinct=True))
        .order_by("-created_at")[:300]
    )
    ctx["all_proposals"] = (
        Proposal.objects.select_related("job", "freelancer", "job__client")
        .order_by("-created_at")[:300]
    )
    ctx["all_contracts"] = (
        Contract.objects.select_related("job", "client", "freelancer")
        .annotate(milestone_count=Count("milestones"))
        .order_by("-created_at")[:300]
    )
    ctx["all_reviews"] = (
        Review.objects.select_related("reviewer", "reviewee")
        .order_by("-created_at")[:300]
    )
    ctx["all_transactions"] = (
        Transaction.objects.select_related("wallet__user")
        .order_by("-created_at")[:300]
    )

    return render(request, "admin/mission_control.html", ctx)


@superuser_required
def analytics_dashboard(request):
    return redirect("mission_control")


# ── Moderation action endpoints ────────────────────────────────────────────────

@superuser_required
@require_POST
def moderate_review_approve(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    review.is_approved = True
    review.save(update_fields=["is_approved"])
    return JsonResponse({"ok": True, "msg": "Review approved"})


@superuser_required
@require_POST
def moderate_review_reject(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    review.is_approved = False
    review.is_public = False
    review.save(update_fields=["is_approved", "is_public"])
    return JsonResponse({"ok": True, "msg": "Review hidden"})


@superuser_required
@require_POST
def moderate_dispute_resolve(request, dispute_id):
    dispute = get_object_or_404(Dispute, id=dispute_id)
    dispute.status = "resolved"
    dispute.resolution = request.POST.get("resolution", "Resolved by admin.")
    dispute.save(update_fields=["status", "resolution"])
    return JsonResponse({"ok": True, "msg": "Dispute resolved"})


@superuser_required
@require_POST
def moderate_job_activate(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    job.status = "active"
    job.save(update_fields=["status"])
    return JsonResponse({"ok": True, "msg": "Job activated"})


@superuser_required
@require_POST
def moderate_job_feature(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    job.is_featured = not job.is_featured
    job.save(update_fields=["is_featured"])
    return JsonResponse({"ok": True, "featured": job.is_featured})


@superuser_required
@require_POST
def moderate_user_verify(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_verified = True
    user.save(update_fields=["is_verified"])
    return JsonResponse({"ok": True, "msg": f"{user.username} verified"})


@superuser_required
@require_POST
def moderate_user_ban(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = False
    user.save(update_fields=["is_active"])
    return JsonResponse({"ok": True, "msg": f"{user.username} banned"})


@superuser_required
@require_POST
def moderate_user_unban(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = True
    user.save(update_fields=["is_active"])
    return JsonResponse({"ok": True, "msg": f"{user.username} unbanned"})


@superuser_required
@require_POST
def moderate_job_delete(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    title = job.title[:40]
    job.delete()
    return JsonResponse({"ok": True, "msg": f"Job '{title}' deleted"})


@superuser_required
@require_POST
def moderate_make_staff(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_staff = not user.is_staff
    user.save(update_fields=["is_staff"])
    action = "made staff" if user.is_staff else "removed from staff"
    return JsonResponse({"ok": True, "msg": f"{user.username} {action}"})
