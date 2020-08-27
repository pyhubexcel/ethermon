# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

from etheremon_lib import config

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'wfi=!_f4r4wy8otc(v5ouazf%in)tks48#)6*he92os61a+o4m'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config.DEBUG

ALLOWED_HOSTS = config.ALLOWED_HOSTS

ROOT_URLCONF = 'etheremon_api.urls'

WSGI_APPLICATION = 'etheremon_api.wsgi.application'

CORS_ORIGIN_REGEX_WHITELIST = config.CORS_ORIGIN_REGEX_WHITELIST
CORS_ORIGIN_WHITELIST = config.CORS_ORIGIN_WHITELIST
CORS_ALLOW_CREDENTIALS = config.CORS_ALLOW_CREDENTIALS


CORS_ALLOW_HEADERS = ['Access-Control-Allow-Headers', 'Origin','Accept', 'X-Requested-With', 'Content-Type', 'Access-Control-Request-Method', 'Access-Control-Request-Headers', 'Authorization']


CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# Application definition

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    # 'social.apps.django_app.default',
    'etheremon_api',
    'etheremon_lib',
    'django_extensions',
    'debug_toolbar',
    'django_pdb'
)

MIDDLEWARE_CLASSES = (
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',

)

INTERNAL_IPS = [
    # ...
    '127.0.0.1',
    'localhost'
    # ...
]

TEMPLATES = [
    {
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

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = config.DATABASES
DATABASE_ROUTERS = ['common.django_model.DatabaseRouter', ]

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Singapore'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = ''

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, '../static').replace('\\','/'),
)
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# logging config
LOGGER_CONFIG = {
    'log_dir': '@stdout' if os.environ.get('DJANGO_LOCALHOST') == 'True' else os.path.join(BASE_DIR, 'log')
}

SESSION_COOKIE_AGE = 86400     # a day
SESSION_COOKIE_SECURE = config.SESSION_COOKIE_SECURE
SESSION_COOKIE_HTTPONLY = config.SESSION_COOKIE_HTTPONLY

CSRF_USE_SESSIONS = False
CSRF_COOKIE_SECURE = True

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)



