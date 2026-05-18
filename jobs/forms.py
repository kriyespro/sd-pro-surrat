from django import forms

from .models import Job


class JobBasicsForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ["title", "description", "category", "skills", "deadline"]


class JobBudgetForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ["pricing_type", "budget_min", "budget_max", "experience_level"]


class JobPreferencesForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ["visibility", "status", "is_featured"]
