"""Google OAuth 2.0 — login / sign-up."""
import logging
import secrets
import urllib.parse

import requests
from django.conf import settings
from django.urls import reverse

from .models import User

log = logging.getLogger(__name__)

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"
SCOPES = "openid email profile"


def google_oauth_enabled():
    return bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET)


def build_redirect_uri(request):
    if getattr(settings, "GOOGLE_REDIRECT_URI", ""):
        uri = settings.GOOGLE_REDIRECT_URI
    else:
        scheme = "https" if request.is_secure() or not settings.DEBUG else request.scheme
        path = reverse("google_callback")
        uri = f"{scheme}://{request.get_host()}{path}"
    log.warning("GOOGLE OAuth redirect_uri = %s", uri)
    return uri


def authorization_url(request, state):
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": build_redirect_uri(request),
        "response_type": "code",
        "scope": SCOPES,
        "state": state,
        "access_type": "online",
        "prompt": "select_account",
    }
    return f"{GOOGLE_AUTH_URL}?{urllib.parse.urlencode(params)}"


def exchange_code(request, code):
    data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": build_redirect_uri(request),
        "grant_type": "authorization_code",
    }
    resp = requests.post(GOOGLE_TOKEN_URL, data=data, timeout=15)
    resp.raise_for_status()
    return resp.json()


def fetch_userinfo(access_token):
    resp = requests.get(
        GOOGLE_USERINFO_URL,
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


def _unique_username(base):
    base = (base or "user")[:30]
    username = base
    n = 1
    while User.objects.filter(username=username).exists():
        username = f"{base}{n}"[:150]
        n += 1
    return username


def get_or_create_user_from_google(userinfo):
    google_id = userinfo.get("sub")
    email = (userinfo.get("email") or "").strip().lower()
    if not google_id or not email:
        raise ValueError("Google did not return a valid account (email required).")

    user = User.objects.filter(google_id=google_id).first()
    if user:
        return user, False

    user = User.objects.filter(email__iexact=email).first()
    if user:
        if not user.google_id:
            user.google_id = google_id
            user.save(update_fields=["google_id"])
        return user, False

    username = _unique_username(email.split("@")[0])
    user = User(
        username=username,
        email=email,
        first_name=userinfo.get("given_name", "")[:150],
        last_name=userinfo.get("family_name", "")[:150],
        google_id=google_id,
        is_verified=bool(userinfo.get("email_verified")),
    )
    user.set_unusable_password()
    user.save()
    return user, True


def new_oauth_state():
    return secrets.token_urlsafe(32)
