from django.contrib import admin
from .models import Plan, Subscription


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "price_monthly",
        "price_yearly",
        "commission_rate",
        "boosted_proposals",
        "is_featured",
    )
    list_filter = ("is_featured",)
    search_fields = ("name",)
    list_editable = ("commission_rate", "is_featured", "boosted_proposals")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "billing_cycle", "status", "current_period_end")
    list_filter = ("status", "billing_cycle", "plan")
    search_fields = ("user__username", "user__email", "razorpay_sub_id")
