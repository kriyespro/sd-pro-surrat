import uuid

from .models import Referral


def generate_code():
    return str(uuid.uuid4()).split("-")[0].upper()


def create_referral(referrer, referred):
    return Referral.objects.create(referrer=referrer, referred=referred, code=generate_code())
