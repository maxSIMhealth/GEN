"""
Django settings for GEN project.

Generated by 'django-admin startproject' using Django 2.1.5
and updated to Django 3.1

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

import json
import logging.config
import os

from django.contrib.messages import constants as messages
from django.utils.log import DEFAULT_LOGGING as LOGGING
from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/
# before deploying to production

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DJANGO_DEBUG', False) == 'True'

ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '127.0.0.1').split(',')

INTERNAL_IPS = os.getenv('DJANGO_INTERNAL_IPS', '127.0.0.1').split(',')

# Email settings for sending error notifications to admins and emails
# to users (e.g., password resets)
ADMINS = [
    ("Admin", os.getenv('DJANGO_ADMIN_EMAIL')),
]
if not DEBUG:
    LOGGING["handlers"]["mail_admins"]["include_html"] = True
    SERVER_EMAIL = os.getenv('SERVER_EMAIL')
    DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')

#
# Application definition
#

INSTALLED_APPS = [
    "admin_interface",
    "modeltranslation",
    "colorfield",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "widget_tweaks",
    "embed_video",
    "django_bootstrap5",
    "vote",
    "debug_toolbar",
    "social_django",
    "crispy_forms",
    "crispy_bootstrap5",
    "adminsortable2",
    "django_extensions",
    "import_export",
    "sri",
    "rosetta",
    "maintenance_mode",
    "tinymce",
    "storages",
    "django_tables2",
    "core",
    "accounts",
    "courses",
    "discussions",
    "dashboard",
    "quiz",
    "videos",
    "content",
    "games"
]

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"

CRISPY_TEMPLATE_PACK = "bootstrap5"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "social_django.middleware.SocialAuthExceptionMiddleware",
    "maintenance_mode.middleware.MaintenanceModeMiddleware",
]

# Provide a lists of languages which your site supports.
LANGUAGES = (
    ("en", _("English")),
    ("fr", _("French")),
)

ROOT_URLCONF = "GEN.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
            ],
        },
    },
]

MESSAGE_TAGS = {
    messages.DEBUG: "secondary",
    messages.INFO: "info",
    messages.SUCCESS: "success",
    messages.WARNING: "warning",
    messages.ERROR: "danger",
}

# Django 3.2 requires defining the default value for auto-created primary keys
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

AUTHENTICATION_BACKENDS = (
    # "social_core.backends.github.GithubOAuth2",
    # "social_core.backends.twitter.TwitterOAuth",
    # "social_core.backends.facebook.FacebookOAuth2",
    # "social_core.backends.google.GoogleOpenId",
    "social_core.backends.google.GoogleOAuth2",
    "django.contrib.auth.backends.ModelBackend",
)

WSGI_APPLICATION = "GEN.wsgi.application"

# Unless there is a good reason for the site to serve other parts of
# itself in a frame, set X_FRAME_OPTIONS to 'DENY'
# django-admin-interface requires this to be set to SAMEORIGIN
X_FRAME_OPTIONS = "SAMEORIGIN"
SILENCED_SYSTEM_CHECKS = ['security.W019']

#
# Database
#

# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('POSTGRES_DB', 'gen_dev'),
        'USER': os.getenv('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'postgres'),
        'HOST': os.getenv('DATABASE_SERVICE', 'postgres'),
        'PORT': os.getenv('DATABASE_PORT', 5432),
        'OPTIONS': json.loads(
            os.getenv('DATABASE_OPTIONS', '{}')
        ),
    }
}

#
# Password validation
#

# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

#
# Internationalization
#

# https://docs.djangoproject.com/en/3.1/topics/i18n/
#
# ISO Language Code Table
# http://www.lingoes.net/en/translator/langcode.htm

LANGUAGE_CODE = "en"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Contains the path list where Django should look into for django.po files for all supported languages
LOCALE_PATHS = (os.path.join(BASE_DIR, "locale"),)

#
# Static files (CSS, JavaScript, Images)
#

# https://docs.djangoproject.com/en/3.1/howto/static-files/

USE_S3 = os.getenv('USE_S3') == 'True'

if USE_S3:
    # Moving static assets to DigitalOcean Spaces as per:
    # https://www.digitalocean.com/community/tutorials/how-to-set-up-object-storage-with-django
    AWS_ACCESS_KEY_ID = os.getenv('STATIC_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('STATIC_SECRET_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('STATIC_BUCKET_NAME')
    AWS_DEFAULT_ACL = 'public-read'
    AWS_S3_ENDPOINT_URL = os.getenv('STATIC_ENDPOINT_URL')
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }
    AWS_LOCATION = os.getenv('GEN_INSTANCE_NAME')
    # Don't protect s3 urls and handle that in the model
    AWS_QUERYSTRING_AUTH = False

    # S3 static settings
    STATICFILES_STORAGE = 'GEN.storage_backends.StaticStorage'
    AWS_STATIC_LOCATION = f'{AWS_LOCATION}/static'
    STATIC_URL = f'{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/{AWS_STATIC_LOCATION}/'
    STATIC_ROOT = 'static/'
    
    # S3 public media settings
    DEFAULT_FILE_STORAGE = 'GEN.storage_backends.MediaStorage'
    AWS_MEDIA_LOCATION = f'{AWS_LOCATION}/media/public'
    MEDIA_URL = f'{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/{AWS_MEDIA_LOCATION}/'
    MEDIA_ROOT = 'media/'

else:
    GEN_HOME = os.getenv('GEN_HOME')
    STATIC_URL = 'static/'
    STATIC_ROOT = f'{GEN_HOME}/static/'
    MEDIA_URL = 'media/'
    MEDIA_ROOT = f'{GEN_HOME}/media/'
    # STATICFILES_DIRS = (os.path.join(BASE_DIR, 'core/static'),)

#
# Login settings
#

LOGIN_URL = "login"
LOGOUT_URL = "logout"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"

if not DEBUG:
    # Security / HTTPS / TLS
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_DOMAIN = os.getenv('CSRF_COOKIE_DOMAIN')
    CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS').split(',')
    SESSION_EXPIRE_AT_BROWSER_CLOSE = True
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_HSTS_PRELOAD = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_REFERRER_POLICY = "same-origin"
    os.environ["wsgi.url_scheme"] = "https"
else:
    CORS_REPLACE_HTTPS_REFERER = False
    HOST_SCHEME = "http://"
    SECURE_PROXY_SSL_HEADER = None
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_HSTS_SECONDS = None
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_FRAME_DENY = False
    os.environ["wsgi.url_scheme"] = "http"

#
# E-mail backend
#

EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
SENDGRID_TRACK_EMAIL_OPENS = True
SENDGRID_TRACK_CLICKS_HTML = False
SENDGRID_TRACK_CLICKS_PLAIN = False
# Toggle sandbox mode (when running in DEBUG mode)
SENDGRID_SANDBOX_MODE_IN_DEBUG = DEBUG
# echo to stdout or any other file-like object that is passed
# to the backend via the stream kwarg.
SENDGRID_ECHO_TO_STDOUT = DEBUG

#
# Maintenance mode settings
#

# complete list available at
# https://github.com/fabiocaccamo/django-maintenance-mode#configuration-optional

# if True the maintenance-mode will be activated
MAINTENANCE_MODE = None

# by default, a file named "maintenance_mode_state.txt" will be created in the settings.py directory
# you can customize the state file path in case the default one is not writable
if not DEBUG:
    MAINTENANCE_MODE_STATE_FILE_PATH = 'maintenance_mode_state.txt'

# if True admin site will not be affected by the maintenance-mode page
MAINTENANCE_MODE_IGNORE_ADMIN_SITE = True

# if True the staff will not see the maintenance-mode page
MAINTENANCE_MODE_IGNORE_STAFF = False

# if True the superuser will not see the maintenance-mode page
MAINTENANCE_MODE_IGNORE_SUPERUSER = False

# if True the maintenance mode will not return 503 response while running tests
# useful for running tests while maintenance mode is on, before opening the site to public use
MAINTENANCE_MODE_IGNORE_TESTS = False

#
# Debug toolbar settings
#

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda _request: DEBUG
}

#
# Logging Configuration
#

# Clear prev config
LOGGING_CONFIG = None

# Get loglevel from env
LOGLEVEL = os.getenv('DJANGO_LOGLEVEL', 'info').upper()

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'format': '%(asctime)s %(levelname)s [%(name)s:%(lineno)s] %(module)s %(process)d %(thread)d %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console',
        },
    },
    'loggers': {
        '': {
            'level': LOGLEVEL,
            'handlers': ['console', ],
        },
    },
})

#
# Social authentication settings
#
# Documentation:
# https://python-social-auth.readthedocs.io/en/latest/configuration/settings.html
# https://python-social-auth.readthedocs.io/en/latest/pipeline.html
USE_SOCIAL_AUTH = os.getenv('USE_SOCIAL_AUTH', 'False') == 'True'
USE_SOCIAL_AUTH_ONLY = os.getenv('USE_SOCIAL_AUTH_ONLY', 'False') == 'True'
SOCIAL_AUTH_JSONFIELD_ENABLED = True
SOCIAL_AUTH_LOGIN_ERROR_URL = "/settings/"
SOCIAL_AUTH_LOGIN_REDIRECT_URL = "home"
SOCIAL_AUTH_RAISE_EXCEPTIONS = False
SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL = True
SOCIAL_AUTH_ADMIN_USER_SEARCH_FIELDS = ["username", "first_name", "email"]

# SOCIAL_AUTH_GITHUB_KEY = os.getenv('SOCIAL_AUTH_GITHUB_KEY')
# SOCIAL_AUTH_GITHUB_SECRET = os.getenv('SOCIAL_AUTH_GITHUB_SECRET')
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.getenv('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.getenv('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET')
SOCIAL_AUTH_GOOGLE_OAUTH2_EXTRA_DATA = ["first_name", "last_name"]

USE_SOCIAL_AUTH_WHITELIST = os.getenv('USE_SOCIAL_AUTH_WHITELIST', 'False') == 'True'
if USE_SOCIAL_AUTH_WHITELIST:
    SOCIAL_AUTH_GOOGLE_OAUTH2_WHITELISTED_DOMAINS = os.getenv('SOCIAL_AUTH_GOOGLE_OAUTH2_WHITELISTED_DOMAINS').split(',')

SOCIAL_AUTH_PIPELINE = (
    # Get the information we can about the user and return it in a simple
    # format to create the user instance later. On some cases the details are
    # already part of the auth response from the provider, but sometimes this
    # could hit a provider API.
    "social_core.pipeline.social_auth.social_details",
    # Get the social uid from whichever service we're authing through. The uid is
    # the unique identifier of the given user in the provider.
    "social_core.pipeline.social_auth.social_uid",
    # Verifies that the current auth process is valid within the current
    # project, this is where emails and domains whitelists are applied (if
    # defined).
    "social_core.pipeline.social_auth.auth_allowed",
    # Checks if the current social-account is already associated in the site.
    "social_core.pipeline.social_auth.social_user",
    # Make up a username for this person, appends a random string at the end if
    # there's any collision.
    "social_core.pipeline.user.get_username",
    # Send a validation email to the user to verify its email address.
    # Disabled by default.
    # 'social_core.pipeline.mail.mail_validation',
    # Associates the current social details with another user account with
    # a similar email address. Disabled by default.
    "social_core.pipeline.social_auth.associate_by_email",
    # Create a user account if we haven't found one yet.
    "social_core.pipeline.user.create_user",
    # Create the record that associates the social account with the user.
    "social_core.pipeline.social_auth.associate_user",
    # Populate the extra_data field in the social record with the values
    # specified by settings (and the default ones like access_token, etc).
    "social_core.pipeline.social_auth.load_extra_data",
    # Update the user record with any changed info from the auth service.
    "social_core.pipeline.user.user_details",
)

#
# TinyMCE
#
TINYMCE_DEFAULT_CONFIG = {
    # 'selector': 'textarea',
    'cleanup_on_startup': True,
    'custom_undo_redo_levels': 20,
    # 'theme': 'modern',
    'plugins': '''
            textcolor save link image media preview codesample contextmenu
            table code lists fullscreen insertdatetime searchreplace wordcount visualblocks
            visualchars code autolink lists charmap print anchor
            ''',
    'toolbar1': '''
            fullscreen | bold italic underline | styleselect | fontsizeselect |
            forecolor | alignleft aligncenter alignright alignjustify | indent outdent |
            bullist numlist table | link image media | codesample |
            visualblocks visualchars | charmap hr pagebreak nonbreaking anchor | insertdatetime |
            searchreplace | code
            ''',
    'contextmenu': 'formats | link image | code',
    'menubar': False,
    'statusbar': True,
    'height': 400,
}
TINYMCE_SPELLCHECKER = False

#
# GEN Settings
#
SUPPORT_EMAILS = os.getenv('SUPPORT_EMAILS').split(',')
VALID_EMAIL_DOMAINS = os.getenv('VALID_EMAIL_DOMAINS').split(',')