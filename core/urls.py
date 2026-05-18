from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .admin_views import (
    mission_control, analytics_dashboard,
    moderate_review_approve, moderate_review_reject,
    moderate_dispute_resolve,
    moderate_job_activate, moderate_job_feature, moderate_job_delete,
    moderate_user_verify, moderate_user_ban, moderate_user_unban, moderate_make_staff,
)
from jobs import views as job_views
from proposals import views as proposal_views
from contracts import views as contract_views

urlpatterns = [
    path('admin/', mission_control, name='mission_control'),
    path('sd/analytics/', analytics_dashboard, name='admin_analytics'),
    path('sd/moderate/review/<int:review_id>/approve/', moderate_review_approve, name='moderate_review_approve'),
    path('sd/moderate/review/<int:review_id>/reject/', moderate_review_reject, name='moderate_review_reject'),
    path('sd/moderate/dispute/<int:dispute_id>/resolve/', moderate_dispute_resolve, name='moderate_dispute_resolve'),
    path('sd/moderate/job/<int:job_id>/activate/', moderate_job_activate, name='moderate_job_activate'),
    path('sd/moderate/job/<int:job_id>/feature/', moderate_job_feature, name='moderate_job_feature'),
    path('sd/moderate/job/<int:job_id>/delete/', moderate_job_delete, name='moderate_job_delete'),
    path('sd/moderate/user/<int:user_id>/verify/', moderate_user_verify, name='moderate_user_verify'),
    path('sd/moderate/user/<int:user_id>/ban/', moderate_user_ban, name='moderate_user_ban'),
    path('sd/moderate/user/<int:user_id>/unban/', moderate_user_unban, name='moderate_user_unban'),
    path('sd/moderate/user/<int:user_id>/staff/', moderate_make_staff, name='moderate_make_staff'),
    path('sd/', admin.site.urls),
    path('', include('users.urls')),            # /, /auth/, /dashboard/, /profile/
    path('jobs/', include('jobs.urls')),         # /jobs/browse/, /jobs/post/
    path('browse/', include('jobs.urls')),       # /browse/ shortcut
    path('proposals/', include('proposals.urls')),
    path('contracts/', include('contracts.urls')),
    path('payments/', include('payments.urls')), # /payments/
    path('messages/', include('messaging.urls')),# /messages/
    path('reviews/', include('reviews.urls')),
    path('notifications/', include('notifications.urls')),
    path('referral/', include('referrals.urls')),# /referral/
    path('', include('billing.urls')),           # /pricing/
    path('search/', job_views.search_results, name='search'),
    path('category/<slug:slug>/', job_views.category_view, name='category'),
    path('dashboard/proposals/', proposal_views.dashboard_proposals, name='dashboard_proposals_root'),
    path('milestones/<int:milestone_id>/submit/', contract_views.submit_milestone, name='submit_milestone_root'),
    path('milestones/<int:milestone_id>/approve/', contract_views.approve_milestone, name='approve_milestone_root'),
    path('milestones/<int:milestone_id>/revision/', contract_views.revision_request, name='revision_milestone_root'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
