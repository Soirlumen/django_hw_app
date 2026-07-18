from pathlib import Path
import sys
import environ
import os
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    DATABASE_URL=(str, f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
    SECRET_KEY=(str, "your-secret-key"),
    MAX_UPLOAD_FILE_SIZE_MB=(int, 2),
    MAX_UPLOAD_FILES_NUMBER=(int, 5),
    MAX_HOMEWORK_LENGTH=(int, 30000),
)
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG")
ALLOWED_HOSTS = ["*"]

env_file = BASE_DIR / '.env'
if os.path.exists(env_file):
    environ.Env.read_env(str(env_file))

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    ## dodatečně instalované appky
    "crispy_forms",
    "crispy_bootstrap5",
    'django_bootstrap_icons',
    "phonenumber_field",
    "whitenoise.runserver_nostatic",
    'django_filters',
    ## moje appky
    "hw",
    "accounts",
    "news",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

ROOT_URLCONF = "django_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                'django.template.context_processors.media',
                'django.template.context_processors.i18n',
            ],
        },
    },
]

WSGI_APPLICATION = "django_project.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    "default": env.db(),
}

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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


LANGUAGE_CODE = "cs"

TIME_ZONE = "Europe/Prague" #kvůli deadline things

USE_I18N = True
USE_TZ = True
LANGUAGES = [
    ("cs", "Čeština"),
    ("en", "English"),
]
LOCALE_PATHS = [
    BASE_DIR / "locale",
]

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"] 
STATIC_ROOT = BASE_DIR / "staticfiles" 

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {  
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",  
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "accounts.CustomUser"

LOGIN_REDIRECT_URL = "success_login"
LOGOUT_REDIRECT_URL = "login"
SIGNUP_REDIRECT_URL = "login"

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"
PHONENUMBER_DEFAULT_REGION = "CZ" 
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# omezení souborů
MAX_UPLOAD_FILE_SIZE_MB = env("MAX_UPLOAD_FILE_SIZE_MB")
MAX_UPLOAD_FILE_SIZE = MAX_UPLOAD_FILE_SIZE_MB * (1024**2)  # Přepočet na bajty zůstává v Pythonu
MAX_UPLOAD_FILES_NUMBER = env("MAX_UPLOAD_FILES_NUMBER")
MAX_HOMEWORK_LENGTH = env("MAX_HOMEWORK_LENGTH")

if 'test' in sys.argv:
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.InMemoryStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }