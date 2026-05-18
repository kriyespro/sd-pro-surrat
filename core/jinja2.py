"""
Jinja2 environment for SuratPro.
Exposes: static, url, csrf_input, csrf_token, request, user, messages
"""
from django.templatetags.static import static as django_static
from django.urls import reverse
from jinja2 import Environment


def static(path):
    return django_static(path)


def url(viewname, *args, **kwargs):
    """Reverse a named URL. Supports {{ url('job_detail', job_id=job.id) }}."""
    if args and kwargs:
        raise ValueError("url() accepts either positional args or keyword args, not both.")
    if kwargs:
        return reverse(viewname, kwargs=kwargs)
    if args:
        return reverse(viewname, args=args)
    return reverse(viewname)


def environment(**options):
    env = Environment(**options)
    env.globals.update({
        'static': static,
        'url': url,
    })
    return env
