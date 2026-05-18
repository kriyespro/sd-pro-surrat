from django.core.management.base import BaseCommand
from billing.models import Plan


PLANS = [
    {
        "name": "Free",
        "price_monthly": 0,
        "price_yearly": 0,
        "max_jobs_per_month": 3,
        "commission_rate": 15,
        "boosted_proposals": 0,
        "is_featured": False,
        "is_active": True,
    },
    {
        "name": "Pro",
        "price_monthly": 999,
        "price_yearly": 9999,
        "max_jobs_per_month": 20,
        "commission_rate": 10,
        "boosted_proposals": 5,
        "is_featured": True,
        "is_active": True,
    },
    {
        "name": "Enterprise",
        "price_monthly": 2499,
        "price_yearly": 24999,
        "max_jobs_per_month": 0,
        "commission_rate": 5,
        "boosted_proposals": 50,
        "is_featured": True,
        "is_active": True,
    },
]


class Command(BaseCommand):
    help = "Seed subscription plans (Free / Pro / Business)."

    def handle(self, *args, **options):
        for data in PLANS:
            plan, created = Plan.objects.update_or_create(
                name=data["name"],
                defaults={k: v for k, v in data.items() if k != "name"},
            )
            action = "created" if created else "updated"
            self.stdout.write(self.style.SUCCESS(f"  {action}: {plan.name} — ₹{plan.price_monthly}/mo"))
        self.stdout.write(self.style.SUCCESS("Plans seeded."))
