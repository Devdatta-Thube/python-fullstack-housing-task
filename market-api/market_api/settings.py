"""
Minimal Django settings for market-api.

No database is used — the dataset is a 50-row CSV loaded into memory.
We keep Django's auth/admin apps out to stay lean, and only install
DRF + cors-headers + our one app.
"""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "dev-only-insecure-key-replace-for-real-deploys",
)
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"

# Compose sets DJANGO_ALLOWED_HOSTS=market-api,localhost,127.0.0.1
ALLOWED_HOSTS = [
    h.strip()
    for h in os.environ.get(
        "DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1"
    ).split(",")
    if h.strip()
] or ["*"]

INSTALLED_APPS = [
    # Django contrib — only what DRF needs.
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",
    "corsheaders",
    # Local
    "market",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "market_api.urls"
WSGI_APPLICATION = "market_api.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {},
    },
]

# We have no DB, but Django refuses to start without one configured.
# Use an in-memory SQLite that we never touch.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# In-process cache for CSV-derived aggregates. A single worker is assumed;
# if we scale out workers, switch to Redis (or just let each worker compute
# its own — the dataset is 50 rows, recompute is free).
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "market-aggregates",
    }
}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = False
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
    ],
    "DEFAULT_PAGINATION_CLASS": None,
    "UNAUTHENTICATED_USER": None,
}

# Wide-open CORS; the portal and interview-demo browsers are the only callers.
CORS_ALLOW_ALL_ORIGINS = True

# ------ Service configuration (read by market.services / market.ml_client) ------

DATASET_PATH = Path(
    os.environ.get("DATASET_PATH", BASE_DIR / "data" / "housing.csv")
)
ML_API_URL = os.environ.get("ML_API_URL", "http://localhost:8000")
ML_API_TIMEOUT = float(os.environ.get("ML_API_TIMEOUT", "5.0"))
AGGREGATE_CACHE_TTL = int(os.environ.get("AGGREGATE_CACHE_TTL", "300"))

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "%(asctime)s %(levelname)s %(name)s: %(message)s"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {"handlers": ["console"], "level": "INFO"},
}
