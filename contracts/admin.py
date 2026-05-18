from django.contrib import admin
from .models import Contract, Deliverable, Milestone, RevisionRequest

admin.site.register(Contract)
admin.site.register(Milestone)
admin.site.register(Deliverable)
admin.site.register(RevisionRequest)
