from django.conf import settings


def site_settings(request):
    from users.google_auth import google_oauth_enabled
    return {
        "STATIC_CSS": getattr(settings, "STATIC_CSS", "css/style.css"),
        "DEBUG": settings.DEBUG,
        "GOOGLE_LOGIN_ENABLED": google_oauth_enabled(),
    }
