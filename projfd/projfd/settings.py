# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import getpass, imp, os
from django.utils.crypto import get_random_string
from os.path import expanduser
from subprocess import check_output

from .additional_settings.cors import *
from .additional_settings.drf import *
from .additional_settings.swagger import *
from .dynamic_settings import *

try:
    from .additional_settings.secrets import SECRET_KEY
except Exception as e:
    raise Exception("You have not created a SECRET_KEY.  Please run python3 firstdraft/python_scripts/intialize.py")


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SETTINGS_DIR = os.path.dirname(__file__)
PROJECT_PATH = os.path.join(SETTINGS_DIR, os.pardir)
PROJECT_PATH = os.path.abspath(PROJECT_PATH)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            "django.contrib.auth.context_processors.auth",
            "django.template.context_processors.debug",
            "django.template.context_processors.i18n",
            "django.template.context_processors.media",
            "django.template.context_processors.static",
            "django.template.context_processors.tz",
            "django.contrib.messages.context_processors.messages"
            #"social_django.context_processors.backends",
            #"social_django.context_processors.login_redirect"
        ]
    },
},]


ALLOWED_HOSTS = ["0.0.0.0", "52.23.197.49"]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'django_extensions',
    'django_filters',
    'mod_wsgi.server',
    'rest_framework',
    'rest_framework_gis',
    'rest_framework_swagger',
    'appfd',
    'behave_django',
    'apifd',
    'timezone_field',
    "corsheaders"
]

if DEBUG:
    pass


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',    
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'corsheaders.middleware.CorsPostCsrfMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware'
    #'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if DEBUG:
    pass

ROOT_URLCONF = 'projfd.urls'

AUTHENTICATION_BACKENDS = [
   #'social_core.backends.facebook.FacebookOAuth2',
   #'social_core.backends.google.GoogleOAuth2',
   #'social_core.backends.twitter.TwitterOAuth',
   'django.contrib.auth.backends.ModelBackend'
]

WSGI_APPLICATION = 'projfd.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'dbfd',
        'USER': getpass.getuser(), # gets current user running this file
        'PORT': 5432,
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_ROOT = "/home/usrfd/firstdraft/projfd/static/"
STATIC_URL = '/static/'

DEFAULT_CHARSET = 'utf-8'
FILE_CHARSET = 'utf-8'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media')



# For Emailing
"""
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = EMAIL_HOST_PASSWORD
EMAIL_PORT = 587
EMAIL_USE_TLS = True
ACCOUNT_ACTIVATION_DAYS = 7
REGISTRATION_OPEN=True
"""


# For Python Social Auth
LOGIN_REDIRECT_URL = '/'

SENDFILE_BACKEND = 'sendfile.backends.mod_wsgi'
SENDFILE_ROOT = 'home/usrfd/maps'
SENDFILE_URL = '/maps'


#://pythonhosted.org/django-guardian/configuration.html 
ANONYMOUS_USER_ID = -1

#http://python-social-auth.readthedocs.io/en/latest/configuration/django.html
#SOCIAL_AUTH_ADMIN_USER_SEARCH_FIELDS = ['username', 'first_name', 'email']


CONTROLCENTER_DASHBOARDS = (
    'projfd.dashboards.MyDashboard',
)

FILEPATH_OF_MARGE_TRAINING_DATA = "/tmp/marge_training_data.tsv"

USER_HOME_DIRECTORY = expanduser("~/")