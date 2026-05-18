from django.utils import timezone
from .models import Subscription


def get_user_plan(user):
    sub = getattr(user, "subscription", None)
    if sub and sub.status == "active":
        return sub.plan
    return None


def check_feature_access(user):
    sub = getattr(user, "subscription", None)
    return bool(sub and sub.status == "active")


def can_post_job(user):
    """Return (allowed: bool, reason: str). 0 = unlimited."""
    plan = get_user_plan(user)
    if plan is None or plan.max_jobs_per_month == 0:
        return True, ""
    from jobs.models import Job
    month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    count = Job.objects.filter(client=user, created_at__gte=month_start).count()
    if count >= plan.max_jobs_per_month:
        return False, f"Your {plan.name} plan allows {plan.max_jobs_per_month} jobs/month. Upgrade to post more."
    return True, ""


def can_submit_proposal(user):
    """Return (allowed: bool, reason: str). Free users: 5/day cap."""
    from proposals.models import BidLimit
    plan = get_user_plan(user)
    daily_limit = 5 if plan is None else (0 if plan.max_jobs_per_month == 0 else 10)
    if daily_limit == 0:
        return True, ""
    today = timezone.localdate()
    limit_obj, _ = BidLimit.objects.get_or_create(freelancer=user, date=today)
    if limit_obj.count >= daily_limit:
        return False, f"Daily bid limit ({daily_limit}) reached. Upgrade your plan for more bids."
    return True, ""


def increment_bid_count(user):
    from proposals.models import BidLimit
    today = timezone.localdate()
    obj, _ = BidLimit.objects.get_or_create(freelancer=user, date=today)
    obj.count += 1
    obj.save(update_fields=["count"])


def create_subscription(user, plan, cycle="monthly"):
    sub, _ = Subscription.objects.update_or_create(
        user=user,
        defaults={"plan": plan, "billing_cycle": cycle, "status": "active"},
    )
    return sub
