from django.contrib import admin
from .models import BidLimit, Proposal

admin.site.register(Proposal)
admin.site.register(BidLimit)
