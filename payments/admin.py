from django.contrib import admin
from .models import Dispute, Transaction, Wallet


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("user", "balance", "escrow_balance", "updated_at")
    search_fields = ("user__username", "user__email")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "wallet", "type", "amount", "status", "created_at")
    list_filter = ("type", "status", "created_at")
    search_fields = ("wallet__user__username", "ref_id")


@admin.action(description="Move disputes to in review")
def mark_in_review(modeladmin, request, queryset):
    queryset.update(status="in_review")


@admin.action(description="Resolve disputes")
def mark_resolved(modeladmin, request, queryset):
    queryset.update(status="resolved")


@admin.register(Dispute)
class DisputeAdmin(admin.ModelAdmin):
    list_display = ("id", "contract", "raised_by", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("raised_by__username", "contract__job__title", "reason")
    actions = (mark_in_review, mark_resolved)
