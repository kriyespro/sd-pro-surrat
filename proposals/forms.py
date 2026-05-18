from django import forms

from .models import Proposal


class ProposalForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = ["cover_letter", "proposed_rate", "delivery_days"]


class CounterOfferForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = ["cover_letter", "proposed_rate", "delivery_days"]
