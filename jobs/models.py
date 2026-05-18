from django.db import models
from django.conf import settings

from users.models import Category, Skill


class Job(models.Model):
    PRICING_CHOICES = [("fixed", "Fixed"), ("hourly", "Hourly")]
    EXPERIENCE_CHOICES = [("entry", "Entry"), ("mid", "Mid"), ("expert", "Expert")]
    VISIBILITY_CHOICES = [("public", "Public"), ("invite", "Invite Only")]
    STATUS_CHOICES = [("draft", "Draft"), ("active", "Active"), ("closed", "Closed"), ("completed", "Completed")]

    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="jobs")
    title = models.CharField(max_length=180)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    skills = models.ManyToManyField(Skill, blank=True)
    pricing_type = models.CharField(max_length=12, choices=PRICING_CHOICES, default="fixed")
    budget_min = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    budget_max = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deadline = models.DateField(null=True, blank=True)
    experience_level = models.CharField(max_length=12, choices=EXPERIENCE_CHOICES, default="mid")
    visibility = models.CharField(max_length=12, choices=VISIBILITY_CHOICES, default="public")
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="draft")
    is_featured = models.BooleanField(default=False)
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
