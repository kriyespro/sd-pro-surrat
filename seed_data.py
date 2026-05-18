"""
SuratPro Data Seeder
Run: python manage.py shell < seed_data.py
Or:  python manage.py runscript seed_data (if django-extensions installed)
Or directly: python seed_data.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from users.models import (
    User, FreelancerProfile, Category, Skill, PortfolioItem, Certification
)
from jobs.models import Job
from proposals.models import Proposal
from contracts.models import Contract, Milestone
from reviews.models import Review
from notifications.models import Notification, NotificationPreference
from messaging.models import Thread, Message
from payments.models import Wallet, Transaction
from referrals.models import Referral, PayoutRequest

User = get_user_model()

print("\n🌱 SuratPro Seeder Starting...\n")

# ── 1. Categories ─────────────────────────────────────────────────────────────
print("📁 Creating categories...")

cats_data = [
    ("Web & App Dev",       "💻", "web-app-dev",       1),
    ("Design & Creative",   "🎨", "design-creative",   2),
    ("Textile & Fashion",   "🧵", "textile-fashion",   3),
    ("Finance & Accounts",  "📊", "finance-accounts",  4),
    ("Content & Writing",   "✍️", "content-writing",   5),
    ("Social & Marketing",  "📱", "social-marketing",  6),
    ("Diamond & Jewellery", "💎", "diamond-jewellery", 7),
    ("Architecture & Civil","🏗️", "architecture-civil",8),
]

categories = {}
for name, icon, slug, order in cats_data:
    cat, created = Category.objects.get_or_create(
        slug=slug, defaults={'name': name, 'icon': icon, 'order': order}
    )
    categories[slug] = cat
    print(f"  {'✅' if created else '⏭'} {icon} {name}")

# ── 2. Skills ─────────────────────────────────────────────────────────────────
print("\n🔧 Creating skills...")

skills_data = [
    ("Python",          "web-app-dev"),
    ("Django",          "web-app-dev"),
    ("React.js",        "web-app-dev"),
    ("Node.js",         "web-app-dev"),
    ("Flutter",         "web-app-dev"),
    ("PostgreSQL",      "web-app-dev"),
    ("UI/UX Design",    "design-creative"),
    ("Figma",           "design-creative"),
    ("Adobe Illustrator","design-creative"),
    ("Logo Design",     "design-creative"),
    ("Textile Design",  "textile-fashion"),
    ("Garment Export",  "textile-fashion"),
    ("Embroidery",      "textile-fashion"),
    ("GST Filing",      "finance-accounts"),
    ("Tally ERP",       "finance-accounts"),
    ("Bookkeeping",     "finance-accounts"),
    ("SEO Writing",     "content-writing"),
    ("Blog Writing",    "content-writing"),
    ("Copywriting",     "content-writing"),
    ("Instagram Ads",   "social-marketing"),
    ("Meta Ads",        "social-marketing"),
    ("YouTube SEO",     "social-marketing"),
    ("Diamond Grading", "diamond-jewellery"),
    ("Jewellery CAD",   "diamond-jewellery"),
    ("AutoCAD",         "architecture-civil"),
    ("3D Rendering",    "architecture-civil"),
]

skills = {}
for skill_name, cat_slug in skills_data:
    skill, created = Skill.objects.get_or_create(
        name=skill_name,
        defaults={'category': categories[cat_slug]}
    )
    skills[skill_name] = skill
    print(f"  {'✅' if created else '⏭'} {skill_name}")

# ── 3. Admin / Superuser ──────────────────────────────────────────────────────
print("\n👤 Creating admin...")
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@suratpro.in',
        password='admin1234',
        first_name='Admin',
        last_name='SuratPro',
    )
    print("  ✅ admin / admin1234")
else:
    print("  ⏭ admin already exists")

# ── 4. Test Client ────────────────────────────────────────────────────────────
print("\n👤 Creating test client...")
client_data = {
    'username': 'rahul_shah',
    'email': 'rahul@example.com',
    'password': 'Test1234!',
    'first_name': 'Rahul',
    'last_name': 'Shah',
    'role': 'client',
    'phone': '9898989898',
    'city': 'Surat',
    'bio': 'Textile entrepreneur from Surat looking for top freelance talent.',
    'is_verified': True,
}
if not User.objects.filter(username=client_data['username']).exists():
    client = User.objects.create_user(**{k: v for k, v in client_data.items() if k != 'password'})
    client.set_password(client_data['password'])
    client.save()
    print(f"  ✅ {client_data['username']} / {client_data['password']}")
else:
    client = User.objects.get(username=client_data['username'])
    print(f"  ⏭ {client_data['username']} already exists")


def get_freelancer_by_username(username):
    return User.objects.filter(username=username, role="freelancer").first()


client_user = client

# ── 5. Test Freelancers ───────────────────────────────────────────────────────
print("\n👤 Creating freelancers...")

freelancers_data = [
    {
        'username': 'karan_patel',
        'email': 'karan@example.com',
        'password': 'Test1234!',
        'first_name': 'Karan',
        'last_name': 'Patel',
        'role': 'freelancer',
        'phone': '9898001001',
        'city': 'Adajan, Surat',
        'bio': 'Full-stack developer with 5+ years building Django & React apps. Worked with 120+ clients across India.',
        'is_verified': True,
        'profile': {
            'title': 'Full-Stack Developer',
            'hourly_rate': 2200,
            'min_project': 15000,
            'availability': 'available',
            'response_time': '~1 hour',
            'experience_years': 5,
            'jobs_completed': 127,
            'avg_rating': 4.8,
            'total_reviews': 98,
            'skills': ['Python', 'Django', 'React.js', 'PostgreSQL'],
        }
    },
    {
        'username': 'nidhi_desai',
        'email': 'nidhi@example.com',
        'password': 'Test1234!',
        'first_name': 'Nidhi',
        'last_name': 'Desai',
        'role': 'freelancer',
        'phone': '9898002002',
        'city': 'Vesu, Surat',
        'bio': 'UI/UX designer & brand identity expert. Helped 200+ businesses build their visual identity.',
        'is_verified': True,
        'profile': {
            'title': 'UI/UX Designer & Brand Expert',
            'hourly_rate': 1500,
            'min_project': 8000,
            'availability': 'available',
            'response_time': '~30 mins',
            'experience_years': 4,
            'jobs_completed': 210,
            'avg_rating': 5.0,
            'total_reviews': 210,
            'skills': ['UI/UX Design', 'Figma', 'Logo Design', 'Adobe Illustrator'],
        }
    },
    {
        'username': 'dev_mehta',
        'email': 'dev@example.com',
        'password': 'Test1234!',
        'first_name': 'Dev',
        'last_name': 'Mehta',
        'role': 'freelancer',
        'phone': '9898003003',
        'city': 'Athwa, Surat',
        'bio': 'Flutter developer specialising in cross-platform apps. 4+ years delivering pixel-perfect mobile experiences.',
        'is_verified': True,
        'profile': {
            'title': 'Flutter & Mobile Developer',
            'hourly_rate': 1800,
            'min_project': 20000,
            'availability': 'busy',
            'response_time': '~2 hours',
            'experience_years': 4,
            'jobs_completed': 156,
            'avg_rating': 4.9,
            'total_reviews': 156,
            'skills': ['Flutter', 'Node.js', 'PostgreSQL'],
        }
    },
    {
        'username': 'priya_vora',
        'email': 'priya@example.com',
        'password': 'Test1234!',
        'first_name': 'Priya',
        'last_name': 'Vora',
        'role': 'freelancer',
        'phone': '9898004004',
        'city': 'Katargam, Surat',
        'bio': 'Chartered Accountant helping businesses with GST, TDS, and financial planning.',
        'is_verified': True,
        'profile': {
            'title': 'Chartered Accountant & GST Expert',
            'hourly_rate': 1200,
            'min_project': 5000,
            'availability': 'available',
            'response_time': '~1 hour',
            'experience_years': 7,
            'jobs_completed': 340,
            'avg_rating': 4.9,
            'total_reviews': 340,
            'skills': ['GST Filing', 'Tally ERP', 'Bookkeeping'],
        }
    },
    {
        'username': 'aisha_khan',
        'email': 'aisha@example.com',
        'password': 'Test1234!',
        'first_name': 'Aisha',
        'last_name': 'Khan',
        'role': 'freelancer',
        'phone': '9898005005',
        'city': 'Rander, Surat',
        'bio': 'Digital marketing expert. Running Meta & Google ads for textile and e-commerce brands since 2019.',
        'is_verified': True,
        'profile': {
            'title': 'Digital Marketing & Meta Ads Expert',
            'hourly_rate': 950,
            'min_project': 6000,
            'availability': 'available',
            'response_time': '~45 mins',
            'experience_years': 5,
            'jobs_completed': 189,
            'avg_rating': 4.9,
            'total_reviews': 189,
            'skills': ['Meta Ads', 'Instagram Ads', 'YouTube SEO'],
        }
    },
    {
        'username': 'vijay_prajapati',
        'email': 'vijay@example.com',
        'password': 'Test1234!',
        'first_name': 'Vijay',
        'last_name': 'Prajapati',
        'role': 'freelancer',
        'phone': '9898006006',
        'city': 'Udhna, Surat',
        'bio': 'Textile designer with deep roots in Surat\'s fabric industry. Specialises in saree & dress material design.',
        'is_verified': True,
        'profile': {
            'title': 'Textile & Saree Designer',
            'hourly_rate': 1400,
            'min_project': 10000,
            'availability': 'available',
            'response_time': '~2 hours',
            'experience_years': 8,
            'jobs_completed': 312,
            'avg_rating': 5.0,
            'total_reviews': 312,
            'skills': ['Textile Design', 'Garment Export', 'Embroidery'],
        }
    },
]

for fl_data in freelancers_data:
    profile_data = fl_data.pop('profile')
    fl_skills = profile_data.pop('skills')

    if not User.objects.filter(username=fl_data['username']).exists():
        user = User.objects.create_user(**{k: v for k, v in fl_data.items() if k != 'password'})
        user.set_password(fl_data['password'])
        user.save()

        profile = FreelancerProfile.objects.create(user=user, **profile_data)
        for skill_name in fl_skills:
            if skill_name in skills:
                profile.skills.add(skills[skill_name])

        # Portfolio items
        PortfolioItem.objects.create(
            freelancer=profile,
            title=f"{user.first_name}'s Top Project",
            description=f"A high-quality project delivered by {user.first_name} showcasing expertise in {fl_skills[0]}.",
            order=1
        )

        # Certification
        Certification.objects.create(
            freelancer=profile,
            title=f"{fl_skills[0]} Professional Certificate",
            issuer="Udemy / Coursera",
            year=2022
        )

        print(f"  ✅ {fl_data['username']} ({profile_data['title']}) — {fl_data['password']}")
    else:
        print(f"  ⏭ {fl_data['username']} already exists")

# ── 6. Threads & Messages ─────────────────────────────────────────────────────
print("\n📌 Creating sample jobs...")
job_specs = [
    {
        "title": "Build Textile Supplier Dashboard",
        "description": "Need a secure dashboard for supplier onboarding, inventory visibility, and GST export reports.",
        "pricing_type": "fixed",
        "budget_min": 25000,
        "budget_max": 45000,
        "experience_level": "mid",
        "skills": ["Django", "React.js", "PostgreSQL"],
    },
    {
        "title": "Design Premium Brand Kit",
        "description": "Looking for logo, social creatives, and typography kit for a Surat jewelry startup.",
        "pricing_type": "fixed",
        "budget_min": 12000,
        "budget_max": 22000,
        "experience_level": "entry",
        "skills": ["UI/UX Design", "Logo Design", "Adobe Illustrator"],
    },
    {
        "title": "Meta Ads Growth Sprint",
        "description": "Run 30-day performance campaign for local apparel brand with weekly optimization.",
        "pricing_type": "hourly",
        "budget_min": 800,
        "budget_max": 1500,
        "experience_level": "expert",
        "skills": ["Meta Ads", "Instagram Ads", "Copywriting"],
    },
]
jobs = []
for spec in job_specs:
    job, _ = Job.objects.get_or_create(
        client=client_user,
        title=spec["title"],
        defaults={
            "description": spec["description"],
            "pricing_type": spec["pricing_type"],
            "budget_min": spec["budget_min"],
            "budget_max": spec["budget_max"],
            "experience_level": spec["experience_level"],
            "status": "active",
        },
    )
    for sk in spec["skills"]:
        if sk in skills:
            job.skills.add(skills[sk])
    jobs.append(job)
print(f"  ✅ jobs ready ({len(jobs)})")

print("\n📝 Creating proposals...")
proposal_specs = [
    ("karan_patel", jobs[0], 38000, 10, "accepted"),
    ("nidhi_desai", jobs[1], 18000, 7, "accepted"),
    ("aisha_khan", jobs[2], 1200, 30, "shortlisted"),
]
proposals = []
for username, job, rate, days, status in proposal_specs:
    freelancer = get_freelancer_by_username(username)
    if not freelancer:
        continue
    # Delete all existing proposals for this job+freelancer, then create clean one
    Proposal.objects.filter(job=job, freelancer=freelancer).delete()
    proposal = Proposal.objects.create(
        job=job,
        freelancer=freelancer,
        cover_letter=f"Hi, I can deliver {job.title.lower()} with clear milestones and weekly updates.",
        proposed_rate=rate,
        delivery_days=days,
        status=status,
    )
    proposals.append(proposal)
print(f"  ✅ proposals ready ({len(proposals)})")

print("\n📄 Creating contracts & milestones...")
contracts = []
for proposal in proposals:
    if proposal.status != "accepted":
        continue
    contract, _ = Contract.objects.get_or_create(
        job=proposal.job,
        proposal=proposal,
        client=client_user,
        freelancer=proposal.freelancer,
        defaults={
            "total_value": proposal.proposed_rate,
            "status": "active",
            "signed_by_client": True,
            "signed_by_freelancer": True,
            "signed_at": timezone.now(),
        },
    )
    Milestone.objects.get_or_create(
        contract=contract,
        order=1,
        defaults={
            "title": "Discovery & Planning",
            "description": "Requirements freeze and initial architecture.",
            "amount": float(proposal.proposed_rate) * 0.4,
            "status": "released",
        },
    )
    Milestone.objects.get_or_create(
        contract=contract,
        order=2,
        defaults={
            "title": "Execution & Delivery",
            "description": "Main implementation, QA, and handover.",
            "amount": float(proposal.proposed_rate) * 0.6,
            "status": "approved",
        },
    )
    contracts.append(contract)
print(f"  ✅ contracts ready ({len(contracts)})")

print("\n⭐ Creating reviews...")
for contract in contracts:
    Review.objects.get_or_create(
        contract=contract,
        reviewer=client_user,
        reviewee=contract.freelancer,
        defaults={
            "rating": 5,
            "feedback": "Professional communication, clear delivery milestones, and quality output.",
            "is_public": True,
            "is_approved": True,
        },
    )
print(f"  ✅ reviews ready ({Review.objects.count()})")

print("\n🔔 Creating notifications...")
for title, body, url in [
    ("New proposal received", "Karan Patel sent a proposal for your dashboard job.", "/dashboard/"),
    ("Milestone approved", "Milestone 2 is ready for fund release.", "/payments/"),
    ("Referral reward added", "You earned a referral bonus this week.", "/referral/"),
]:
    Notification.objects.get_or_create(
        user=client_user,
        title=title,
        defaults={"type": "system", "body": body, "url": url, "is_read": False},
    )
NotificationPreference.objects.get_or_create(user=client_user)
print("  ✅ notifications ready")

print("\n💬 Creating message threads...")
seed_freelancers = User.objects.filter(role="freelancer")[:3]
for freelancer in seed_freelancers:
    thread = Thread.objects.filter(participants=client_user).filter(participants=freelancer).first()
    if not thread:
        thread = Thread.objects.create()
        thread.participants.add(client_user, freelancer)
    if not thread.messages.exists():
        Message.objects.create(thread=thread, sender=freelancer, body=f"Hi {client_user.first_name}, I can help with your project.")
        Message.objects.create(thread=thread, sender=client_user, body="Great, please share your timeline and estimate.")
        Message.objects.create(thread=thread, sender=freelancer, body="Sure. I can start this week and deliver in milestones.")
    print(f"  ✅ thread with {freelancer.username}")

# ── 7. Wallet & Transactions ──────────────────────────────────────────────────
print("\n💳 Creating wallet transactions...")
wallet, _ = Wallet.objects.get_or_create(user=client_user)
if wallet.balance == 0 and wallet.escrow_balance == 0:
    wallet.balance = 180000
    wallet.escrow_balance = 45000
    wallet.save()
for tx_type, amount, status in [
    ("topup", 50000, "success"),
    ("escrow", 12000, "success"),
    ("release", 15000, "success"),
    ("refund", 5000, "success"),
]:
    Transaction.objects.get_or_create(
        wallet=wallet,
        type=tx_type,
        amount=amount,
        defaults={"status": status, "ref_id": f"SP-{tx_type.upper()}-{amount}"},
    )
print("  ✅ wallet and transactions ready")

# ── 8. Referrals ───────────────────────────────────────────────────────────────
print("\n🎁 Creating referrals...")
for freelancer in User.objects.filter(role="freelancer")[:4]:
    ref, _ = Referral.objects.get_or_create(
        referrer=client_user,
        referred=freelancer,
        defaults={"code": f"REF{client_user.id}{freelancer.id}"},
    )
    if not ref.signup_bonus_paid:
        ref.signup_bonus_paid = True
        ref.first_job_bonus_paid = freelancer.id % 2 == 0
        ref.save()
PayoutRequest.objects.get_or_create(
    user=client_user,
    amount=1000,
    status="pending",
    upi_id="rahul@upi",
)
print("  ✅ referrals and payout request ready")

# ── Summary ───────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("✅ SEED COMPLETE")
print("="*60)
print(f"  Categories:   {Category.objects.count()}")
print(f"  Skills:       {Skill.objects.count()}")
print(f"  Users total:  {User.objects.count()}")
print(f"  Freelancers:  {FreelancerProfile.objects.count()}")
print(f"  Portfolio:    {PortfolioItem.objects.count()}")
print(f"  Certs:        {Certification.objects.count()}")
print(f"  Jobs:         {Job.objects.count()}")
print(f"  Proposals:    {Proposal.objects.count()}")
print(f"  Contracts:    {Contract.objects.count()}")
print(f"  Milestones:   {Milestone.objects.count()}")
print(f"  Threads:      {Thread.objects.count()}")
print(f"  Messages:     {Message.objects.count()}")
print(f"  Transactions: {Transaction.objects.count()}")
print(f"  Referrals:    {Referral.objects.count()}")
print(f"  Reviews:      {Review.objects.count()}")
print(f"  Notifications:{Notification.objects.count()}")
print("\nLOGIN CREDENTIALS:")
print("  Admin:           admin / admin1234  →  /sd/")
print("  Client:          rahul_shah / Test1234!  →  /dashboard/")
print("  Freelancer 1:    karan_patel / Test1234! →  /profile/karan_patel/")
print("  Freelancer 2:    nidhi_desai / Test1234! →  /profile/nidhi_desai/")
print("  Freelancer 3:    dev_mehta / Test1234!   →  /profile/dev_mehta/")
print("  Freelancer 4:    priya_vora / Test1234!  →  /profile/priya_vora/")
print("  Freelancer 5:    aisha_khan / Test1234!  →  /profile/aisha_khan/")
print("  Freelancer 6:    vijay_prajapati / Test1234! → /profile/vijay_prajapati/")
print("="*60)
