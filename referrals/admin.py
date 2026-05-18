from django.contrib import admin
from .models import AffiliateEarning, PayoutRequest, Referral

admin.site.register(Referral)
admin.site.register(AffiliateEarning)
admin.site.register(PayoutRequest)
