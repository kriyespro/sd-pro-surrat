from django.db import models
from django.conf import settings

from contracts.models import Contract, Milestone


class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wallet")
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    escrow_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Wallet({self.user})"


class Transaction(models.Model):
    TYPE_CHOICES = [("topup", "Topup"), ("escrow", "Escrow"), ("release", "Release"), ("refund", "Refund"), ("payout", "Payout")]
    STATUS_CHOICES = [("pending", "Pending"), ("success", "Success"), ("failed", "Failed")]
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="transactions")
    type = models.CharField(max_length=12, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    ref_id = models.CharField(max_length=120, blank=True)
    contract = models.ForeignKey(Contract, on_delete=models.SET_NULL, null=True, blank=True)
    milestone = models.ForeignKey(Milestone, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class Dispute(models.Model):
    STATUS_CHOICES = [("open", "Open"), ("in_review", "In Review"), ("resolved", "Resolved"), ("closed", "Closed")]
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name="disputes")
    raised_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reason = models.TextField()
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="open")
    resolution = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
