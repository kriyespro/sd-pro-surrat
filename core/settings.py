from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent
try:
    import dj_database_url
except ImportError:  # optional until dependency installed
    dj_database_url = None
try:
    import sentry_sdk
except ImportError:  # optional until dependency installed
    sentry_sdk = None

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = [h.strip() for h in config('ALLOWED_HOSTS', default='127.0.0.1,localhost,testserver').split(',') if h.strip()]

_csrf_origins = config('CSRF_TRUSTED_ORIGINS', default='')
CSRF_TRUSTED_ORIGINS = [o.strip() for o in _csrf_origins.split(',') if o.strip()]

# ── Apps ──────────────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # local
    'users',
    'jobs',
    'proposals',
    'contracts',
    'payments',
    'messaging',
    'reviews',
    'notifications',
    'referrals',
    'billing',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

# ── Templates ─────────────────────────────────────────────────────────────────
TEMPLATES = [
    {
        # Jinja2 — PRIMARY (all .jinja files)
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': False,
        'OPTIONS': {
            'environment': 'core.jinja2.environment',
            'auto_reload': DEBUG,
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.site_settings',
            ],
        },
    },
    {
        # Django Templates — ONLY for admin (/sd/)
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# ── Auth ──────────────────────────────────────────────────────────────────────
AUTH_USER_MODEL = 'users.User'
LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# ── Database ──────────────────────────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
if config("DATABASE_URL", default=""):
    if dj_database_url:
        DATABASES["default"] = dj_database_url.parse(
            config("DATABASE_URL"),
            conn_max_age=600,
            ssl_require=config("DATABASE_SSL_REQUIRE", default=False, cast=bool),
        )
        if not config("DATABASE_SSL_REQUIRE", default=False, cast=bool):
            DATABASES["default"].setdefault("OPTIONS", {})["sslmode"] = "disable"

# ── Password validation ───────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
]

# ── Internationalisation ──────────────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# ── Static & Media ────────────────────────────────────────────────────────────
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_CSS = config('STATIC_CSS', default='css/style.css')
WHITENOISE_MAX_AGE = config('WHITENOISE_MAX_AGE', default=31536000 if not DEBUG else 0, cast=int)
WHITENOISE_MANIFEST_STRICT = DEBUG

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── Razorpay ──────────────────────────────────────────────────────────────────
RAZORPAY_KEY_ID = config('RAZORPAY_KEY_ID', default='')
RAZORPAY_KEY_SECRET = config('RAZORPAY_KEY_SECRET', default='')
RAZORPAY_USE_DUMMY = config('RAZORPAY_USE_DUMMY', default=True, cast=bool)

# ── Site ──────────────────────────────────────────────────────────────────────
SITE_NAME = 'SuratPro'
SITE_TAGLINE = "Surat's #1 Freelance Marketplace"

# ── Google OAuth ──────────────────────────────────────────────────────────────
GOOGLE_CLIENT_ID = config('GOOGLE_CLIENT_ID', default='')
GOOGLE_CLIENT_SECRET = config('GOOGLE_CLIENT_SECRET', default='')
GOOGLE_REDIRECT_URI = config('GOOGLE_REDIRECT_URI', default='')

# ── Production/Infra toggles ──────────────────────────────────────────────────
SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=not DEBUG, cast=bool)
SESSION_COOKIE_SECURE = config("SESSION_COOKIE_SECURE", default=not DEBUG, cast=bool)
CSRF_COOKIE_SECURE = config("CSRF_COOKIE_SECURE", default=not DEBUG, cast=bool)
SECURE_HSTS_SECONDS = config("SECURE_HSTS_SECONDS", default=31536000 if not DEBUG else 0, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = config("SECURE_HSTS_INCLUDE_SUBDOMAINS", default=not DEBUG, cast=bool)
SECURE_HSTS_PRELOAD = config("SECURE_HSTS_PRELOAD", default=not DEBUG, cast=bool)

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    USE_X_FORWARDED_HOST = True
    USE_X_FORWARDED_PORT = True

REDIS_URL = config("REDIS_URL", default="redis://127.0.0.1:6379/1")
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "suratpro-local",
    }
}
if config("USE_REDIS_CACHE", default=False, cast=bool):
    CACHES["default"] = {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
    }

if config("USE_REDIS_SESSIONS", default=False, cast=bool):
    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    SESSION_CACHE_ALIAS = "default"

CELERY_BROKER_URL = config("CELERY_BROKER_URL", default=REDIS_URL)
CELERY_RESULT_BACKEND = config("CELERY_RESULT_BACKEND", default=REDIS_URL)
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE

EMAIL_BACKEND = config("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="no-reply@suratpro.in")

AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME", default="")
AWS_S3_REGION_NAME = config("AWS_S3_REGION_NAME", default="")
AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID", default="")
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY", default="")

SENTRY_DSN = config("SENTRY_DSN", default="")
if sentry_sdk and SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        traces_sample_rate=config("SENTRY_TRACES_SAMPLE_RATE", default=0.0, cast=float),
        send_default_pii=True,
    )
