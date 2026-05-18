from django.db import models
from django.conf import settings


class Plan(models.Model):
    name = models.CharField(max_length=50)
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price_yearly = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_jobs_per_month = models.PositiveIntegerField(default=0)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=15)
    boosted_proposals = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Subscription(models.Model):
    STATUS_CHOICES = [("active", "Active"), ("cancelled", "Cancelled"), ("expired", "Expired")]
    CYCLE_CHOICES = [("monthly", "Monthly"), ("yearly", "Yearly")]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscription")
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True)
    billing_cycle = models.CharField(max_length=12, choices=CYCLE_CHOICES, default="monthly")
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="active")
    current_period_end = models.DateTimeField(null=True, blank=True)
    razorpay_sub_id = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return f"{self.user} - {self.plan}"
