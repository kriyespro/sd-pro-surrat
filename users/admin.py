from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, FreelancerProfile, Skill, Category, PortfolioItem, Certification


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'is_verified', 'created_at']
    list_filter = ['role', 'is_verified', 'is_active']
    actions = ("verify_users", "unverify_users", "ban_users", "unban_users")
    fieldsets = BaseUserAdmin.fieldsets + (
        ('SuratPro', {'fields': ('role', 'phone', 'city', 'bio', 'avatar',
                                  'is_verified', 'referral_code')}),
    )

    @admin.action(description="Mark selected users as verified")
    def verify_users(self, request, queryset):
        queryset.update(is_verified=True)

    @admin.action(description="Remove verified badge from selected users")
    def unverify_users(self, request, queryset):
        queryset.update(is_verified=False)

    @admin.action(description="Ban selected users")
    def ban_users(self, request, queryset):
        queryset.update(is_active=False)

    @admin.action(description="Unban selected users")
    def unban_users(self, request, queryset):
        queryset.update(is_active=True)


@admin.register(FreelancerProfile)
class FreelancerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'hourly_rate', 'availability', 'avg_rating']
    list_filter = ['availability']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'slug', 'order']
    prepopulated_fields = {'slug': ('name',)}


admin.register(Skill)(type('SkillAdmin', (admin.ModelAdmin,), {
    'list_display': ['name', 'category'],
    'search_fields': ['name'],
}))
admin.site.register(PortfolioItem)
admin.site.register(Certification)
