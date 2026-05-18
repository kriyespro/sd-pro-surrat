from django.test import TestCase, override_settings

from billing.models import Plan
from contracts.models import Contract, Milestone
from jobs.models import Job
from messaging.models import Message, Thread
from payments.models import Transaction, Wallet
from proposals.models import Proposal
from referrals.models import Referral
from reviews.models import Review
from users.models import Category, Skill, User


@override_settings(STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage")
class PlannedMvpFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client_user = User.objects.create_user(
            username="client_user",
            password="Test1234!",
            role="client",
            email="client@example.com",
        )
        cls.freelancer_user = User.objects.create_user(
            username="freelancer_user",
            password="Test1234!",
            role="freelancer",
            email="freelancer@example.com",
        )
        cls.admin_user = User.objects.create_superuser(
            username="admin_test",
            password="admin1234",
            email="admin_test@example.com",
        )

        cls.category = Category.objects.create(name="Web Dev", slug="web-dev", icon="💻", order=1)
        cls.skill = Skill.objects.create(name="Django", category=cls.category)
        cls.job = Job.objects.create(
            client=cls.client_user,
            title="Build MVP",
            description="Need an MVP app",
            category=cls.category,
            status="active",
            budget_min=1000,
            budget_max=2000,
        )
        cls.job.skills.add(cls.skill)

        cls.proposal = Proposal.objects.create(
            job=cls.job,
            freelancer=cls.freelancer_user,
            cover_letter="Can do this",
            proposed_rate=1500,
            delivery_days=7,
            status="pending",
        )
        cls.contract = Contract.objects.create(
            job=cls.job,
            proposal=cls.proposal,
            client=cls.client_user,
            freelancer=cls.freelancer_user,
            total_value=1500,
            status="active",
            signed_by_client=False,
            signed_by_freelancer=False,
        )
        cls.milestone = Milestone.objects.create(
            contract=cls.contract,
            title="Phase 1",
            amount=750,
            order=1,
            status="pending",
        )
        cls.thread = Thread.objects.create(contract=cls.contract)
        cls.thread.participants.add(cls.client_user, cls.freelancer_user)
        Message.objects.create(thread=cls.thread, sender=cls.freelancer_user, body="Hello")

        cls.wallet = Wallet.objects.create(user=cls.client_user, balance=10000, escrow_balance=0)
        Transaction.objects.create(wallet=cls.wallet, type="topup", amount=1000, status="success", ref_id="seed")

        Review.objects.create(
            contract=cls.contract,
            reviewer=cls.client_user,
            reviewee=cls.freelancer_user,
            rating=5,
            feedback="Great work",
            is_approved=True,
        )
        Referral.objects.create(
            referrer=cls.client_user,
            referred=cls.freelancer_user,
            code="TESTREF1",
            signup_bonus_paid=True,
            first_job_bonus_paid=False,
        )
        Plan.objects.create(name="Free", price_monthly=0, price_yearly=0, commission_rate=15)

    def _login_client(self):
        self.client.login(username="client_user", password="Test1234!")

    def _login_freelancer(self):
        self.client.login(username="freelancer_user", password="Test1234!")

    def test_public_routes(self):
        for path in ["/", "/browse/", "/auth/login/", "/auth/register/", "/pricing/"]:
            response = self.client.get(path)
            self.assertLess(response.status_code, 400, msg=path)

    def test_client_planned_endpoints(self):
        self._login_client()
        checks = [
            ("get", "/search/"),
            ("get", "/category/web-dev/"),
            ("post", f"/proposals/{self.proposal.id}/accept/"),
            ("post", f"/proposals/{self.proposal.id}/reject/"),
            ("post", f"/proposals/{self.proposal.id}/counter/"),
            ("get", f"/proposals/{self.proposal.id}/"),
            ("get", "/dashboard/proposals/"),
            ("get", f"/contracts/{self.contract.id}/"),
            ("post", f"/contracts/{self.contract.id}/sign/"),
            ("post", f"/milestones/{self.milestone.id}/submit/"),
            ("post", f"/milestones/{self.milestone.id}/approve/"),
            ("post", f"/milestones/{self.milestone.id}/revision/"),
            ("post", "/payments/add/"),
            ("post", "/payments/callback/"),
            ("post", f"/payments/release/{self.milestone.id}/"),
            ("get", "/payments/transactions/"),
            ("post", f"/payments/dispute/{self.contract.id}/"),
            ("get", f"/messages/{self.thread.id}/"),
            ("post", f"/messages/{self.thread.id}/send/"),
            ("post", f"/messages/{self.thread.id}/read/"),
            ("post", f"/messages/start/{self.freelancer_user.id}/"),
            ("get", f"/messages/{self.thread.id}/poll/"),
            ("post", f"/reviews/leave/{self.contract.id}/"),
            ("get", f"/profile/{self.freelancer_user.username}/reviews/"),
            ("get", "/referral/stats/"),
            ("post", "/referral/payout/"),
            ("post", "/billing/checkout/"),
            ("get", "/billing/manage/"),
        ]
        for method, path in checks:
            response = getattr(self.client, method)(path, {})
            self.assertLess(response.status_code, 400, msg=f"{method.upper()} {path}")

    def test_freelancer_can_propose(self):
        self._login_freelancer()
        response = self.client.post(f"/jobs/{self.job.id}/propose/", {})
        self.assertLess(response.status_code, 400)

    def test_dashboard_smoke_client_tabs(self):
        self._login_client()
        for path in (
            "/dashboard/",
            "/dashboard/?page=overview",
            "/dashboard/?page=jobs",
            "/dashboard/?page=proposals",
            "/dashboard/?page=contracts",
            "/dashboard/?page=invalid",
        ):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200, msg=path)

    def test_dashboard_smoke_freelancer_tabs(self):
        self._login_freelancer()
        for path in (
            "/dashboard/",
            "/dashboard/?page=overview",
            "/dashboard/?page=proposals",
            "/dashboard/?page=contracts",
            "/dashboard/?page=jobs",
            "/dashboard/?page=nope",
        ):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200, msg=path)

    def test_admin_analytics_access(self):
        self.client.force_login(self.admin_user)
        response = self.client.get("/sd/analytics/")
        self.assertEqual(response.status_code, 200)
