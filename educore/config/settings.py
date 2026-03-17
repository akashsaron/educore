"""
EduCore School ERP — Production Settings
Django 5.0 | PostgreSQL | Render.com
"""

from pathlib import Path
from decouple import config, Csv
import dj_database_url
from datetime import timedelta

# ── BASE ─────────────────────────────────────────────────────────────

BASE_DIR = Path(**file**).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost', cast=Csv())

# ── APPLICATIONS ─────────────────────────────────────────────────────

INSTALLED_APPS = [
'django.contrib.admin',
'django.contrib.auth',
'django.contrib.contenttypes',
'django.contrib.sessions',
'django.contrib.messages',
'whitenoise.runserver_nostatic',
'django.contrib.staticfiles',

```
# Third-party
'rest_framework',
'rest_framework.authtoken',
'rest_framework_simplejwt',
'rest_framework_simplejwt.token_blacklist',
'corsheaders',
'django_filters',
'import_export',
'django_celery_beat',

# Local apps
'apps.core',
'apps.students',
'apps.teachers',
'apps.attendance',
'apps.fees',
'apps.exams',
'apps.library',
'apps.transport',
'apps.announcements',
```

]

# ── MIDDLEWARE ───────────────────────────────────────────────────────

MIDDLEWARE = [
'django.middleware.security.SecurityMiddleware',
'whitenoise.middleware.WhiteNoiseMiddleware',

```
'corsheaders.middleware.CorsMiddleware',
'django.middleware.common.CommonMiddleware',

'django.contrib.sessions.middleware.SessionMiddleware',
'django.middleware.csrf.CsrfViewMiddleware',

'django.contrib.auth.middleware.AuthenticationMiddleware',
'django.contrib.messages.middleware.MessageMiddleware',

'django.middleware.clickjacking.XFrameOptionsMiddleware',

# Custom middleware (ensure these exist)
'apps.core.middleware.RequestLogMiddleware',
'apps.core.middleware.AuditMiddleware',
```

]

# ── URLS / WSGI ──────────────────────────────────────────────────────

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

# ── TEMPLATES ────────────────────────────────────────────────────────

TEMPLATES = [{
'BACKEND': 'django.template.backends.django.DjangoTemplates',
'DIRS': [BASE_DIR / 'templates'],
'APP_DIRS': True,
'OPTIONS': {
'context_processors': [
'django.template.context_processors.debug',
'django.template.context_processors.request',
'django.contrib.auth.context_processors.auth',
'django.contrib.messages.context_processors.messages',
],
},
}]

# ── DATABASE ─────────────────────────────────────────────────────────

DATABASES = {
'default': dj_database_url.config(
default=config('DATABASE_URL'),
conn_max_age=600,
ssl_require=True
)
}

# ── AUTH ─────────────────────────────────────────────────────────────

AUTH_USER_MODEL = 'core.User'

AUTH_PASSWORD_VALIDATORS = [
{'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
{'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
'OPTIONS': {'min_length': 8}},
{'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
{'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ── DJANGO REST FRAMEWORK ────────────────────────────────────────────

REST_FRAMEWORK = {
'DEFAULT_AUTHENTICATION_CLASSES': [
'rest_framework_simplejwt.authentication.JWTAuthentication',
],
'DEFAULT_PERMISSION_CLASSES': [
'rest_framework.permissions.IsAuthenticated',
],
'DEFAULT_FILTER_BACKENDS': [
'django_filters.rest_framework.DjangoFilterBackend',
'rest_framework.filters.SearchFilter',
'rest_framework.filters.OrderingFilter',
],
'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
'PAGE_SIZE': 25,
}

# ── JWT ──────────────────────────────────────────────────────────────

SIMPLE_JWT = {
'ACCESS_TOKEN_LIFETIME': timedelta(hours=8),
'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
'ROTATE_REFRESH_TOKENS': True,
'BLACKLIST_AFTER_ROTATION': True,
}

# ── CORS ─────────────────────────────────────────────────────────────

CORS_ALLOWED_ORIGINS = config(
'CORS_ALLOWED_ORIGINS',
default='http://localhost:3000',
cast=Csv()
)
CORS_ALLOW_CREDENTIALS = True

# ── STATIC FILES ─────────────────────────────────────────────────────

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ── MEDIA FILES ──────────────────────────────────────────────────────

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ── EMAIL ────────────────────────────────────────────────────────────

EMAIL_BACKEND = config(
'EMAIL_BACKEND',
default='django.core.mail.backends.console.EmailBackend'
)
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='[noreply@educore.in](mailto:noreply@educore.in)')

# ── LOCALIZATION ─────────────────────────────────────────────────────

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── SECURITY ─────────────────────────────────────────────────────────

if not DEBUG:
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# ── LOGGING ──────────────────────────────────────────────────────────

LOGGING = {
'version': 1,
'disable_existing_loggers': False,
'handlers': {
'console': {'class': 'logging.StreamHandler'},
},
'root': {
'handlers': ['console'],
'level': 'INFO',
},
}
