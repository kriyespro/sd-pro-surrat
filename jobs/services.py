from django.db.models import Q

from users.models import FreelancerProfile

from .models import Job


def create_job(client, cleaned_data):
    return Job.objects.create(client=client, **cleaned_data)


def get_client_jobs(client):
    return Job.objects.filter(client=client).order_by("-created_at")


def search_freelancers(q="", category=None, min_rate=None, max_rate=None, min_rating=None, sort="-avg_rating"):
    qs = FreelancerProfile.objects.select_related("user").all()
    if q:
        qs = qs.filter(Q(user__first_name__icontains=q) | Q(user__last_name__icontains=q) | Q(title__icontains=q))
    if category:
        qs = qs.filter(skills__category__slug=category)
    if min_rate is not None:
        qs = qs.filter(hourly_rate__gte=min_rate)
    if max_rate is not None:
        qs = qs.filter(hourly_rate__lte=max_rate)
    if min_rating is not None:
        qs = qs.filter(avg_rating__gte=min_rating)
    return qs.distinct().order_by(sort)
