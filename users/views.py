from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.views.decorators.http import require_POST

from .models import User, FreelancerProfile
from .forms import RegisterForm, LoginForm, FreelancerProfileForm, UserProfileForm, OnboardingStep1Form, OnboardingFreelancerForm
from .services import build_dashboard_context, resolve_dashboard_page
from . import google_auth


def home(request):
    featured_profiles = (
        FreelancerProfile.objects.select_related("user")
        .prefetch_related("skills")
        .order_by("-avg_rating", "-jobs_completed")[:6]
    )
    return render(request, 'pages/home.jinja', {"featured_profiles": featured_profiles})


def register_view(request):
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            if user.role == 'freelancer':
                FreelancerProfile.objects.create(user=user)
            login(request, user)
            if request.headers.get('HX-Request'):
                return HttpResponse('<script>window.location="/onboarding/"</script>')
            return redirect('onboarding')
        if request.headers.get('HX-Request'):
            return render(request, 'partials/_register_form.jinja', {'form': form})
    return render(request, 'pages/auth/login.jinja', {'reg_form': form, 'tab': 'register'})


def login_view(request):
    form = LoginForm(request)
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            if request.headers.get('HX-Request'):
                return HttpResponse('<script>window.location="/dashboard/"</script>')
            return redirect('dashboard')
        if request.headers.get('HX-Request'):
            return render(request, 'partials/_login_form.jinja', {'form': form})
    return render(request, 'pages/auth/login.jinja', {'login_form': form, 'tab': 'login'})


@require_POST
def logout_view(request):
    logout(request)
    return redirect('home')


def google_login_start(request):
    if not google_auth.google_oauth_enabled():
        messages.error(request, "Google sign-in is not configured.")
        return redirect("login")
    state = google_auth.new_oauth_state()
    request.session["google_oauth_state"] = state
    request.session["google_oauth_next"] = request.GET.get("next", "/dashboard/")
    return redirect(google_auth.authorization_url(request, state))


def google_callback(request):
    if not google_auth.google_oauth_enabled():
        messages.error(request, "Google sign-in is not configured.")
        return redirect("login")

    if request.GET.get("error"):
        messages.error(request, "Google sign-in was cancelled.")
        return redirect("login")

    state = request.GET.get("state", "")
    if state != request.session.pop("google_oauth_state", None):
        messages.error(request, "Invalid sign-in session. Please try again.")
        return redirect("login")

    code = request.GET.get("code")
    if not code:
        messages.error(request, "Google did not return an authorization code.")
        return redirect("login")

    try:
        token_data = google_auth.exchange_code(request, code)
        userinfo = google_auth.fetch_userinfo(token_data["access_token"])
        user, created = google_auth.get_or_create_user_from_google(userinfo)
    except Exception:
        messages.error(request, "Could not sign in with Google. Please try again.")
        return redirect("login")

    login(request, user)
    next_url = request.session.pop("google_oauth_next", "/dashboard/")
    if created or not user.onboarding_complete:
        return redirect("onboarding")
    return redirect(next_url)


def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    freelancer_profile = getattr(profile_user, 'freelancer_profile', None) if profile_user.is_freelancer else None
    portfolio_items = []
    certifications = []
    similar_profiles = []
    if freelancer_profile:
        portfolio_items = freelancer_profile.portfolio_items.all().order_by("order", "-id")
        certifications = freelancer_profile.certifications.all().order_by("-year", "-id")
        similar_profiles = (
            FreelancerProfile.objects.select_related("user")
            .exclude(user=profile_user)
            .order_by("-avg_rating", "-jobs_completed")[:2]
        )
    return render(request, 'pages/profile.jinja', {
        'profile_user': profile_user,
        'freelancer_profile': freelancer_profile,
        'portfolio_items': portfolio_items,
        'certifications': certifications,
        'similar_profiles': similar_profiles,
    })


@login_required
def dashboard(request):
    page = resolve_dashboard_page(request.user, request.GET.get('page', 'overview'))
    ctx = build_dashboard_context(request.user)
    ctx['page'] = page
    ctx['today_heading'] = timezone.localdate().strftime('%A, %d %B %Y')
    return render(request, 'pages/dashboard.jinja', ctx)


@login_required
def profile_edit(request):
    user_form = UserProfileForm(instance=request.user)
    fl_form = None
    if request.user.is_freelancer:
        profile, _ = FreelancerProfile.objects.get_or_create(user=request.user)
        fl_form = FreelancerProfileForm(instance=profile)
    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if user_form.is_valid():
            user_form.save()
            if request.user.is_freelancer:
                profile, _ = FreelancerProfile.objects.get_or_create(user=request.user)
                fl_form = FreelancerProfileForm(request.POST, instance=profile)
                if fl_form.is_valid():
                    fl_form.save()
            if request.headers.get('HX-Request'):
                return HttpResponse('<div class="sp-toast">✅ Profile saved!</div>')
            messages.success(request, 'Profile updated.')
            return redirect('dashboard')
    return render(request, 'pages/profile_edit.jinja', {'user_form': user_form, 'fl_form': fl_form})


@login_required
def onboarding(request):
    if request.user.onboarding_complete:
        return redirect('dashboard')
    step = int(request.GET.get('step', 1))
    if request.method == 'POST':
        step = int(request.POST.get('step', 1))
        if step == 1:
            form = OnboardingStep1Form(request.POST, request.FILES, instance=request.user)
            if form.is_valid():
                form.save()
                if request.user.is_freelancer:
                    return redirect('/onboarding/?step=2')
                request.user.onboarding_complete = True
                request.user.save(update_fields=['onboarding_complete'])
                return redirect('dashboard')
            return render(request, 'pages/onboarding.jinja', {'step': 1, 'form': form})
        if step == 2 and request.user.is_freelancer:
            profile, _ = FreelancerProfile.objects.get_or_create(user=request.user)
            form = OnboardingFreelancerForm(request.POST, instance=profile)
            if form.is_valid():
                form.save()
                request.user.onboarding_complete = True
                request.user.save(update_fields=['onboarding_complete'])
                return redirect('dashboard')
            return render(request, 'pages/onboarding.jinja', {'step': 2, 'form': form})
    if step == 2 and request.user.is_freelancer:
        profile, _ = FreelancerProfile.objects.get_or_create(user=request.user)
        form = OnboardingFreelancerForm(instance=profile)
        return render(request, 'pages/onboarding.jinja', {'step': 2, 'form': form})
    form = OnboardingStep1Form(instance=request.user)
    return render(request, 'pages/onboarding.jinja', {'step': 1, 'form': form})
