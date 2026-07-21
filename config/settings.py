"""
G&T OrthoCare — Django settings.
All deployment-specific values come from environment variables (see .env.example).
"""
import os
from pathlib import Path

import dj_database_url
from django.templatetags.static import static  # noqa: F401
from django.urls import reverse_lazy
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# ---------------------------------------------------------------- core
SECRET_KEY = os.getenv("SECRET_KEY", "dev-insecure-key-change-me")
DEBUG = os.getenv("DEBUG", "1") == "1"
ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "*").split(",") if h.strip()]
CSRF_TRUSTED_ORIGINS = [o.strip() for o in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if o.strip()]

INSTALLED_APPS = [
    "unfold",  # must be before django.contrib.admin
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.catalog",
    "apps.orders",
    "apps.content",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.catalog.context_processors.storefront",
            ],
        },
    },
]

# ---------------------------------------------------------------- database
# Default: SQLite (development). On AWS set DATABASE_URL, e.g.
#   postgres://USER:PASSWORD@RDS_HOST:5432/gtorthocare
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------- i18n / tz
LANGUAGE_CODE = "en-us"          # admin chrome language; storefront has its own KA/EN switch
TIME_ZONE = "Asia/Tbilisi"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------- static & media
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = Path(os.getenv("MEDIA_ROOT", BASE_DIR / "media"))

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}
# For S3 media on AWS: pip install django-storages[boto3], then set
# STORAGES["default"]["BACKEND"] = "storages.backends.s3.S3Storage" + AWS_* env vars.

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------- email
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = os.getenv("EMAIL_HOST", "")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "1") == "1"
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@gtorthocare.ge")
ORDER_NOTIFICATION_EMAIL = os.getenv("ORDER_NOTIFICATION_EMAIL", "")

# ---------------------------------------------------------------- security (behind AWS LB)
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "0"))
    # Set to 1 only if HTTPS redirect is NOT already handled by the ALB/CloudFront
    SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "0") == "1"

# ---------------------------------------------------------------- business
SITE_NAME = "G&T OrthoCare"
PHONE_PRIMARY = "+995 514 06 88 06"
PHONE_SECONDARY = "+995 599 07 70 03"
# Dedicated line for the on-call traumatologist service (consultation / home visits).
# Currently the secondary number — change here when a separate line exists.
PHONE_TRAUMA = os.getenv("PHONE_TRAUMA", PHONE_SECONDARY)
# Line for booking a portable X-ray at home.
PHONE_XRAY = os.getenv("PHONE_XRAY", PHONE_PRIMARY)
CONTACT_EMAIL = "info@gtorthocare.ge"
LOW_STOCK_THRESHOLD = 3
FREE_DELIVERY_FROM = 100  # GEL; orders below pay DELIVERY_FEE
DELIVERY_FEE = 5

# ---------------------------------------------------------------- Unfold admin
UNFOLD = {
    "SITE_TITLE": "G&T OrthoCare Admin",
    "SITE_HEADER": "G&T OrthoCare",
    "SITE_SUBHEADER": "ორთოპედიული მაღაზია — Management",
    "SITE_SYMBOL": "medical_services",
    "SITE_URL": "/",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "DASHBOARD_CALLBACK": "config.dashboard.dashboard_callback",
    "COLORS": {
        "primary": {
            "50": "#F0FAFB", "100": "#D9F2F5", "200": "#B4E4EA", "300": "#83CFDA",
            "400": "#45B3C4", "500": "#0E93A6", "600": "#0B7A8A", "700": "#086572",
            "800": "#0A525C", "900": "#0C444D", "950": "#062E35",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "მთავარი — Overview",
                "separator": False,
                "items": [
                    {"title": "Dashboard", "icon": "dashboard", "link": reverse_lazy("admin:index")},
                ],
            },
            {
                "title": "კატალოგი — Catalog",
                "separator": True,
                "items": [
                    {"title": "პროდუქტები / Products", "icon": "inventory_2",
                     "link": reverse_lazy("admin:catalog_product_changelist")},
                    {"title": "კატეგორიები / Categories", "icon": "category",
                     "link": reverse_lazy("admin:catalog_category_changelist")},
                ],
            },
            {
                "title": "მოთხოვნები — Leads",
                "separator": True,
                "items": [
                    {"title": "შეტყობინებები / Messages", "icon": "mail",
                     "link": reverse_lazy("admin:content_contactmessage_changelist")},
                ],
            },
            {
                "title": "კონტენტი — Content",
                "separator": True,
                "items": [
                    {"title": "ბანერები / Banners", "icon": "image",
                     "link": reverse_lazy("admin:content_banner_changelist")},
                    {"title": "ბლოგი / Blog", "icon": "article",
                     "link": reverse_lazy("admin:content_blogpost_changelist")},
                    {"title": "მაღაზიები / Stores", "icon": "storefront",
                     "link": reverse_lazy("admin:content_storelocation_changelist")},
                    {"title": "ხდკ / FAQ", "icon": "quiz",
                     "link": reverse_lazy("admin:content_faq_changelist")},
                    {"title": "ტელეფონები / Site settings", "icon": "settings_phone",
                     "link": reverse_lazy("admin:content_sitesettings_changelist")},
                ],
            },
            {
                "title": "წვდომა — Access",
                "separator": True,
                "items": [
                    {"title": "Users", "icon": "person", "link": reverse_lazy("admin:auth_user_changelist")},
                    {"title": "Groups", "icon": "group", "link": reverse_lazy("admin:auth_group_changelist")},
                ],
            },
        ],
    },
}
