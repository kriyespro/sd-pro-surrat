from django.db.models import Avg

from .models import Review


def get_avg_rating(user):
    return Review.objects.filter(reviewee=user, is_approved=True).aggregate(avg=Avg("rating")).get("avg") or 0
