from django.db import models
from django.conf import settings

from jobs.models import Job
from proposals.models import Proposal


class Contract(models.Model):
    STATUS_CHOICES = [("active", "Active"), ("completed", "Completed"), ("disputed", "Disputed"), ("cancelled", "Cancelled")]
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="contracts")
    proposal = models.ForeignKey(Proposal, on_delete=models.SET_NULL, null=True, blank=True)
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="client_contracts")
    freelancer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="freelancer_contracts")
    total_value = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="active")
    signed_by_client = models.BooleanField(default=False)
    signed_by_freelancer = models.BooleanField(default=False)
    signed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Contract #{self.id} - {self.job.title}"


class Milestone(models.Model):
    STATUS_CHOICES = [("pending", "Pending"), ("submitted", "Submitted"), ("approved", "Approved"), ("released", "Released")]
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name="milestones")
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="pending")
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


class Deliverable(models.Model):
    milestone = models.ForeignKey(Milestone, on_delete=models.CASCADE, related_name="deliverables")
    file = models.FileField(upload_to="deliverables/", blank=True, null=True)
    note = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)


class RevisionRequest(models.Model):
    milestone = models.ForeignKey(Milestone, on_delete=models.CASCADE, related_name="revision_requests")
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
