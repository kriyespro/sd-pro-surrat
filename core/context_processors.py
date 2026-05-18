from django.conf import settings


def site_settings(request):
    return {
        "STATIC_CSS": getattr(settings, "STATIC_CSS", "css/style.css"),
        "DEBUG": settings.DEBUG,
    }
