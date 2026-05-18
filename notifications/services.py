from .models import Notification


def notify(user, type, title, body="", url=""):
    return Notification.objects.create(user=user, type=type, title=title, body=body, url=url)
