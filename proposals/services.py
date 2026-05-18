from .models import Proposal


def send_proposal(job, freelancer, cleaned_data):
    return Proposal.objects.create(job=job, freelancer=freelancer, **cleaned_data)
