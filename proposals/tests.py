from django.test import TestCase, override_settings

from jobs.models import Job
from proposals.models import Proposal
from users.models import Category, Skill, User


@override_settings(STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage")
class ProposalAuthorizationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cat = Category.objects.create(name="Web Dev", slug="web-dev", icon="💻", order=1)
        cls.skill = Skill.objects.create(name="Django", category=cls.cat)

        cls.client_a = User.objects.create_user(
            username="client_a",
            password="Test1234!",
            role="client",
            email="a@example.com",
        )
        cls.client_b = User.objects.create_user(
            username="client_b",
            password="Test1234!",
            role="client",
            email="b@example.com",
        )
        cls.freelancer = User.objects.create_user(
            username="fl_auth",
            password="Test1234!",
            role="freelancer",
            email="fl@example.com",
        )

        cls.job = Job.objects.create(
            client=cls.client_a,
            title="Owner job",
            description="Work",
            category=cls.cat,
            status="active",
            budget_min=1000,
            budget_max=2000,
        )
        cls.job.skills.add(cls.skill)

        cls.proposal = Proposal.objects.create(
            job=cls.job,
            freelancer=cls.freelancer,
            cover_letter="Bid",
            proposed_rate=1500,
            delivery_days=7,
            status="pending",
        )

    def test_freelancer_cannot_accept_reject_counter(self):
        self.client.login(username="fl_auth", password="Test1234!")
        pid = self.proposal.id
        for path in (
            f"/proposals/{pid}/accept/",
            f"/proposals/{pid}/reject/",
            f"/proposals/{pid}/counter/",
        ):
            with self.subTest(path=path):
                r = self.client.post(path, {})
                self.assertEqual(r.status_code, 403)

    def test_other_client_cannot_accept(self):
        self.client.login(username="client_b", password="Test1234!")
        r = self.client.post(f"/proposals/{self.proposal.id}/accept/", {})
        self.assertEqual(r.status_code, 403)

    def test_job_owner_can_accept(self):
        self.client.login(username="client_a", password="Test1234!")
        r = self.client.post(f"/proposals/{self.proposal.id}/accept/", {})
        self.assertEqual(r.status_code, 200)
        self.proposal.refresh_from_db()
        self.assertEqual(self.proposal.status, "accepted")

    def test_job_owner_can_view_proposal_detail(self):
        self.client.login(username="client_a", password="Test1234!")
        r = self.client.get(f"/proposals/{self.proposal.id}/")
        self.assertEqual(r.status_code, 200)

    def test_freelancer_can_view_own_proposal_detail(self):
        self.client.login(username="fl_auth", password="Test1234!")
        r = self.client.get(f"/proposals/{self.proposal.id}/")
        self.assertEqual(r.status_code, 200)

    def test_freelancer_cannot_view_others_proposal_detail(self):
        other_fl = User.objects.create_user(
            username="other_fl",
            password="Test1234!",
            role="freelancer",
            email="ofl@example.com",
        )
        self.client.login(username="other_fl", password="Test1234!")
        r = self.client.get(f"/proposals/{self.proposal.id}/")
        self.assertEqual(r.status_code, 403)

    def test_client_cannot_view_proposal_for_other_clients_job(self):
        self.client.login(username="client_b", password="Test1234!")
        r = self.client.get(f"/proposals/{self.proposal.id}/")
        self.assertEqual(r.status_code, 403)
