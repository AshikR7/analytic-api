import os
from pathlib import Path
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-secret-key-change-me")
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")

INSTALLED_APPS = [
	"django.contrib.admin",
	"django.contrib.auth",
	"django.contrib.contenttypes",
	"django.contrib.sessions",
	"django.contrib.messages",
	"django.contrib.staticfiles",
	"corsheaders",
	"rest_framework",
	"drf_spectacular",
	"apps.accounts",
	"apps.analytics",
]

MIDDLEWARE = [
	"django.middleware.security.SecurityMiddleware",
	"whitenoise.middleware.WhiteNoiseMiddleware",
	"corsheaders.middleware.CorsMiddleware",
	"django.middleware.common.CommonMiddleware",
	"django.middleware.csrf.CsrfViewMiddleware",
	"django.contrib.sessions.middleware.SessionMiddleware",
	"django.contrib.auth.middleware.AuthenticationMiddleware",
	"django.contrib.messages.middleware.MessageMiddleware",
	"django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "analytic_api.urls"

TEMPLATES = [
	{
		"BACKEND": "django.template.backends.django.DjangoTemplates",
		"DIRS": [],
		"APP_DIRS": True,
		"OPTIONS": {
			"context_processors": [
				"django.template.context_processors.debug",
				"django.template.context_processors.request",
				"django.contrib.auth.context_processors.auth",
				"django.contrib.messages.context_processors.messages",
			],
		},
	},
]

WSGI_APPLICATION = "analytic_api.wsgi.application"

DB_VENDOR = os.getenv("DB_VENDOR", "sqlite").lower()
if DB_VENDOR == "sqlite":
	DATABASES = {
		"default": {
			"ENGINE": "django.db.backends.sqlite3",
			"NAME": BASE_DIR / "db.sqlite3",
		}
	}
else:
	DATABASES = {
		"default": {
			"ENGINE": "django.db.backends.postgresql",
			"NAME": os.getenv("POSTGRES_DB", "analytics_db"),
			"USER": os.getenv("POSTGRES_USER", "analytics_user"),
			"PASSWORD": os.getenv("POSTGRES_PASSWORD", "analytics_password"),
			"HOST": os.getenv("POSTGRES_HOST", "localhost"),
			"PORT": os.getenv("POSTGRES_PORT", "5432"),
		}
	}

redis_url = os.getenv("REDIS_URL")
if redis_url:
	CACHES = {
		"default": {
			"BACKEND": "django_redis.cache.RedisCache",
			"LOCATION": redis_url,
			"OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
			"KEY_PREFIX": "analytics",
		}
	}
else:
	CACHES = {
		"default": {
			"BACKEND": "django.core.cache.backends.locmem.LocMemCache",
			"LOCATION": "analytics-local",
		}
	}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

AUTH_PASSWORD_VALIDATORS = [
	{"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
	{"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
	{"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
	{"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_ALLOW_ALL_ORIGINS = True

REST_FRAMEWORK = {
	"DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
	"DEFAULT_AUTHENTICATION_CLASSES": [
		"rest_framework.authentication.SessionAuthentication",
		"rest_framework.authentication.BasicAuthentication",
	],
	"DEFAULT_THROTTLE_CLASSES": [
		"rest_framework.throttling.UserRateThrottle",
		"rest_framework.throttling.AnonRateThrottle",
	],
	"DEFAULT_THROTTLE_RATES": {
		"user": os.getenv("USER_THROTTLE_RATE", "1000/day"),
		"anon": os.getenv("ANON_THROTTLE_RATE", "500/day"),
		"collect": os.getenv("COLLECT_THROTTLE_RATE", "60/second"),
		"analytics": os.getenv("ANALYTICS_THROTTLE_RATE", "20/second"),
	},
}

SPECTACULAR_SETTINGS = {
	"TITLE": "Website Analytics API",
	"DESCRIPTION": "Scalable analytics ingestion and aggregation API.",
	"VERSION": "1.0.0",
	"SERVE_INCLUDE_SCHEMA": False,
}

# Simple flag for Google auth integration placeholder
ENABLE_GOOGLE_AUTH = os.getenv("ENABLE_GOOGLE_AUTH", "false").lower() == "true"


