"""Django settings for the Silent Key backend project."""

from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent.parent


def load_env_file(env_path: Path):
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding='utf-8').splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue

        key, value = line.split('=', 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def env_str(name, default=None, aliases=()):
    for candidate in (name, *aliases):
        value = os.getenv(candidate)
        if value not in (None, ''):
            return value
    return default


def env_bool(name, default=False, aliases=()):
    value = env_str(name, aliases=aliases)
    if value is None:
        return default
    return value.lower() in {'1', 'true', 'yes', 'on'}


def env_int(name, default, aliases=()):
    value = env_str(name, aliases=aliases)
    if value is None:
        return default
    return int(value)


def env_list(name, default=None, aliases=()):
    value = env_str(name, aliases=aliases)
    if value is None:
        return list(default or [])
    return [item.strip() for item in value.split(',') if item.strip()]


class LocalEnv:
    def read_env(self):
        load_env_file(BASE_DIR.parent / '.env')

    def str(self, name, default=None):
        return env_str(name, default=default)

    def bool(self, name, default=False):
        return env_bool(name, default=default)

    def int(self, name, default):
        return env_int(name, default)

    def list(self, name, default=None):
        return env_list(name, default=default)


env = LocalEnv()
env.read_env()
# Build paths inside the project like this: BASE_DIR / 'subdir'.

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str("SECRET_KEY")
if not SECRET_KEY or len(SECRET_KEY) < 50:
    raise ValueError("SECRET_KEY must be set and at least 50 characters long")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", False)  # Default to False for security

CANONICAL_HOST = env.str("CANONICAL_HOST", "identity.silentkey.me")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", ["localhost", "127.0.0.1", CANONICAL_HOST])


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.identity.apps.IdentityConfig',  # SilentKey Identity Management App
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

ASGI_APPLICATION = 'config.asgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

# Check if we should use migration user (for running migrations)
USE_MIGRATION_USER = env.bool("USE_MIGRATION_USER", False)

if USE_MIGRATION_USER:
    DB_USER = env.str("MIGRATION_DB_USER", "sk_migration_user")
    DB_PASSWORD = env.str("MIGRATION_DB_PASSWORD") or env.str("sk_migration_password")  # No default - fail fast if missing
else:
    DB_USER = env.str("DB_USER", "sk_app_user")
    DB_PASSWORD = env.str("DB_PASSWORD") or env.str("sk_app_password")  # No default - fail fast if missing

DB_NAME = env.str("DB_NAME", "silentkey_identity")
AUDIT_DB_NAME = env.str("AUDIT_DB_NAME", "silentkey_audit")
AUDIT_DB_USER = env.str("AUDIT_DB_USER", DB_USER)
AUDIT_DB_PASSWORD = env.str("AUDIT_DB_PASSWORD") or env.str("sk_readonly_password") or DB_PASSWORD
DB_CONNECT_TIMEOUT = env.int("DB_CONNECT_TIMEOUT", 10)
DB_CONN_MAX_AGE = env.int("DB_CONN_MAX_AGE", 600)

LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": DB_NAME,
        "USER": DB_USER,
        "PASSWORD": DB_PASSWORD,
        "HOST": env.str("DB_HOST", "localhost"),
        "PORT": env.int("DB_PORT", 5432),
        "CONN_MAX_AGE": DB_CONN_MAX_AGE,
        "CONN_HEALTH_CHECKS": True,
        "OPTIONS": {
            "options": "-c search_path=identity,public",
            "connect_timeout": DB_CONNECT_TIMEOUT,
        }
    },
    "audit": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": AUDIT_DB_NAME,
        "USER": AUDIT_DB_USER,
        "PASSWORD": AUDIT_DB_PASSWORD,
        "HOST": env.str("DB_HOST", "localhost"),
        "PORT": env.int("DB_PORT", 5432),
        "CONN_MAX_AGE": DB_CONN_MAX_AGE,
        "CONN_HEALTH_CHECKS": True,
        "OPTIONS": {
            "options": "-c search_path=audit,public",
            "connect_timeout": DB_CONNECT_TIMEOUT,
        }
    }
}


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_USER_MODEL = 'identity.User'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files (uploaded by users)
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Security Settings
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", False)
SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", False)
CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE", False)
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", 0)
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", [f"https://{CANONICAL_HOST}"])

SECURE_PROXY_SSL_HEADER = (
    'HTTP_X_FORWARDED_PROTO',
    'https',
) if env.bool("USE_PROXY_SSL_HEADER", False) else None

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': env.str('LOG_LEVEL', 'INFO'),
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'silentkey.log',
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'security.log',
            'maxBytes': 1024 * 1024 * 15,
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
        'django.security': {
            'handlers': ['security_file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'identity': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}