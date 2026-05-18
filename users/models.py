from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


class User(AbstractUser):
    ROLE_CHOICES = [('client', 'Client'), ('freelancer', 'Freelancer')]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')
    phone = models.CharField(max_length=15, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, default='Surat')
    bio = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    onboarding_complete = models.BooleanField(default=False)
    referral_code = models.CharField(max_length=20, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.username} ({self.role})'

    @property
    def initials(self):
        parts = self.get_full_name().split()
        if len(parts) >= 2:
            return f'{parts[0][0]}{parts[1][0]}'.upper()
        return self.username[:2].upper()

    @property
    def is_freelancer(self):
        return self.role == 'freelancer'

    @property
    def is_client(self):
        return self.role == 'client'


class Category(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=10, default='💼')
    slug = models.SlugField(unique=True)
    order = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['order']

    def __str__(self):
        return self.name


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL,
                                  null=True, blank=True)

    def __str__(self):
        return self.name


class FreelancerProfile(models.Model):
    AVAILABILITY_CHOICES = [
        ('available', 'Available'),
        ('busy', 'Busy'),
        ('offline', 'Offline'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                 related_name='freelancer_profile')
    title = models.CharField(max_length=150, blank=True)
    skills = models.ManyToManyField(Skill, blank=True)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2,
                                       default=0)
    min_project = models.DecimalField(max_digits=10, decimal_places=2,
                                       default=0)
    availability = models.CharField(max_length=20,
                                     choices=AVAILABILITY_CHOICES,
                                     default='available')
    response_time = models.CharField(max_length=50, blank=True,
                                      default='~1 hour')
    experience_years = models.IntegerField(default=0)
    portfolio_url = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    jobs_completed = models.IntegerField(default=0)
    success_rate = models.DecimalField(max_digits=5, decimal_places=2,
                                        default=100)
    avg_rating = models.DecimalField(max_digits=3, decimal_places=1,
                                      default=0)
    total_reviews = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.user.username} — {self.title}'


class PortfolioItem(models.Model):
    freelancer = models.ForeignKey(FreelancerProfile,
                                    on_delete=models.CASCADE,
                                    related_name='portfolio_items')
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='portfolio/', blank=True, null=True)
    url = models.URLField(blank=True)
    tags = models.ManyToManyField(Skill, blank=True)
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.title


class Certification(models.Model):
    freelancer = models.ForeignKey(FreelancerProfile,
                                    on_delete=models.CASCADE,
                                    related_name='certifications')
    title = models.CharField(max_length=200)
    issuer = models.CharField(max_length=150)
    year = models.IntegerField()

    def __str__(self):
        return f'{self.title} — {self.issuer}'
