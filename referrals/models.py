from django.db import models
from django.conf import settings

from payments.models import Transaction


class Referral(models.Model):
    referrer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="referrals_sent")
    referred = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="referred_by")
    code = models.CharField(max_length=24, unique=True)
    signup_bonus_paid = models.BooleanField(default=False)
    first_job_bonus_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("referrer", "referred")

    def __str__(self):
        return f"{self.referrer} -> {self.referred}"


class AffiliateEarning(models.Model):
    TYPE_CHOICES = [("signup", "Signup"), ("first_job", "First Job"), ("commission", "Commission")]
    referral = models.ForeignKey(Referral, on_delete=models.CASCADE, related_name="earnings")
    type = models.CharField(max_length=16, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class PayoutRequest(models.Model):
    STATUS_CHOICES = [("pending", "Pending"), ("processing", "Processing"), ("paid", "Paid")]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payout_requests")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="pending")
    upi_id = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
