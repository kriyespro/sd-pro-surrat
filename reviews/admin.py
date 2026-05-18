from django.contrib import admin
from .models import Review


@admin.action(description="Approve selected reviews")
def approve_reviews(modeladmin, request, queryset):
    queryset.update(is_approved=True)


@admin.action(description="Unapprove selected reviews")
def unapprove_reviews(modeladmin, request, queryset):
    queryset.update(is_approved=False)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "reviewer", "reviewee", "rating", "is_public", "is_approved", "created_at")
    list_filter = ("is_approved", "is_public", "rating", "created_at")
    search_fields = ("reviewer__username", "reviewee__username", "feedback")
    actions = (approve_reviews, unapprove_reviews)
