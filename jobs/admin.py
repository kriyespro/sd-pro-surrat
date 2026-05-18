from django.contrib import admin
from .models import Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "client", "pricing_type", "status", "created_at")
    list_filter = ("pricing_type", "status", "is_featured")
    search_fields = ("title", "description", "client__username")
    list_editable = ("status",)
    actions = ("mark_featured", "mark_unfeatured")

    @admin.action(description="Mark selected jobs as featured")
    def mark_featured(self, request, queryset):
        queryset.update(is_featured=True)

    @admin.action(description="Mark selected jobs as not featured")
    def mark_unfeatured(self, request, queryset):
        queryset.update(is_featured=False)
