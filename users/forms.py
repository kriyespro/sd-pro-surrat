from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, FreelancerProfile


class RegisterForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        widget=forms.HiddenInput()
    )
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
    phone = forms.CharField(max_length=15, required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email',
                  'phone', 'role', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'sp-field'})


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'sp-field'})


class FreelancerProfileForm(forms.ModelForm):
    class Meta:
        model = FreelancerProfile
        fields = ['title', 'hourly_rate', 'min_project',
                  'availability', 'response_time', 'experience_years',
                  'portfolio_url', 'linkedin']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'sp-field'})


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'city', 'profile_summary', 'bio', 'avatar']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'sp-field'})
        self.fields['profile_summary'].widget.attrs.update({
            'rows': 3,
            'placeholder': 'Write 3 sentences that describe you as a professional...',
        })
        self.fields['profile_summary'].label = 'Profile Summary (3 sentences)'


class OnboardingStep1Form(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'city', 'profile_summary', 'bio']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'sp-field'})
        self.fields['profile_summary'].widget.attrs.update({
            'rows': 3,
            'placeholder': 'Write 3 sentences that describe you as a professional...',
        })
        self.fields['profile_summary'].label = 'Profile Summary (3 sentences)'
        self.fields['bio'].widget.attrs.update({'rows': 3, 'placeholder': 'Tell clients about yourself...'})
        self.fields['city'].widget.attrs.update({'placeholder': 'e.g. Surat, Gujarat'})


class OnboardingFreelancerForm(forms.ModelForm):
    class Meta:
        model = FreelancerProfile
        fields = ['title', 'hourly_rate', 'min_project', 'availability', 'experience_years']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'sp-field'})
        self.fields['title'].widget.attrs.update({'placeholder': 'e.g. Full-Stack Developer'})
