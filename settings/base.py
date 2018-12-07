import logging
import os

logging.log(logging.INFO, 'loading settings for ' + __name__)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_ROOT = BASE_DIR

DEVELOPMENT = True
DISABLE_ADMIN_NOTIFICATION = False

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 't8%+b87azv!0)#)bc^x!1h*m(ar#z7flxls!r6mu*+pj6n_q!4'

# SECURITY WARNING: don't run with debug turned on in production!
ALLOWED_HOSTS = ['*', ]

SITE_ID = 1

# Application definition
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django.contrib.humanize',
    # 3rd Party Applications
    'filebrowser',
    'suit',
    'django.contrib.admin',
    'reversion',
    'classytags',
    'easy_thumbnails',
    'pytz',
    'front',
    # My Applications
    'dashboard',
    'navigation',
    'page_content',
    'webapp',
    'webapp_admin',
    'announcement',
    'violation',
    'service_provider',
    'community',
    'neighbor',
    'reservation',
    'dues',
    'contact',
    'external_services',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'neighbor.middleware.choose_community.NeighborMiddleware'
)

from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP

TEMPLATE_CONTEXT_PROCESSORS = TCP + (
    'django.core.context_processors.request',
)

ROOT_URLCONF = 'webapp.urls'

WSGI_APPLICATION = 'webapp.wsgi.application'

# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Chicago'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')
MEDIA_UPLOAD_PATH = os.path.join(MEDIA_ROOT, '/media/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')
STATIC_URL = '/static/'

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, "templates"),
)

FILE_UPLOAD_PERMISSIONS = 0644

SESSION_COOKIE_AGE = 3600
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(filename)s %(funcName)s %(lineno)d %(message)s'
        },
        'normal': {
            'format': '%(levelname)s %(asctime)s %(funcName)s %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'console': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': True,
        },
        'webapp': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': True,
        },
        '': {
            'handlers': ['console'],
            'level': 'ERROR',
        },
    }
}

SUIT_CONFIG = {
    'ADMIN_NAME': 'RCN Community',
    'HEADER_DATE_FORMAT': 'l, F jS, Y',
    'HEADER_TIME_FORMAT': 'h:i a',
    'SHOW_REQUIRED_ASTERISK': True,  # Default True
    'CONFIRM_UNSAVED_CHANGES': True,  # Default True
    'SEARCH_URL': '/admin/auth/user/',
    'MENU_ICONS': {
        'sites': 'icon-leaf',
        'auth': 'icon-lock',
    },
    'MENU_OPEN_FIRST_CHILD': True,  # Default True
    'MENU': (
        {'app': 'auth', 'label': 'Administration', 'icon': 'icon-lock', 'models': ('user', 'group', 'neighbor.transactions', 'neighbor.purchasereport')},
        {'app': 'community', 'icon': 'icon-globe', 'label': 'Communities', 'models': ('community', 'neighbor.calendarevent', 'document', 'contact.contactlead')},
        {'app': 'neighbor', 'icon': 'icon-user', 'label': 'Neighbors', 'models': ('neighbor',)},
        {'app': 'violation', 'icon': 'icon-thumbs-down', 'label': 'Violations'},
        {'app': 'reservation', 'icon': 'icon-calendar', 'label': 'Reservations'},
        {'app': 'announcement', 'icon': 'icon-tasks', 'label': 'Announcements'},
        {'app': 'service_provider', 'icon': 'icon-info-sign', 'label': 'Service Providers'},
        {'app': 'navigation', 'icon': 'icon-list'},
        {'app': 'categories', 'icon': 'icon-th'},
        {'app': 'page_content', 'label': 'Page Content', 'icon': 'icon-file', 'models': ('logo', 'webpage', 'footer', 'modalsuccess', 'billboard', 'minibillboard')},
        {'app': 'staff', 'icon': 'icon-asterisk', 'label': 'Staff'},
        {'label': 'Site Media', 'icon': 'icon-picture', 'url': '/admin/filebrowser/browse/'},
        'sites',
    ),
    'LIST_PER_PAGE': 30
}

FILEBROWSER_SUIT_TEMPLATE = True

DJANGO_FRONT_EDITOR_OPTIONS = {
    'filebrowserBrowseUrl': '/admin/filebrowser/browse/?pop=3'
}

LOGIN_URL = '/login/'

THUMBNAIL_DEBUG = True
THUMBNAIL_ALIASES = {
    '': {
        'avatar': {'size': (50, 50), 'crop': True},
    }
}

# image upload limit, in MB
MAX_FILESIZE = 10.0

GOOGLE_DRIVE_CREDENTIAL_FILE = os.path.join(PROJECT_ROOT, 'settings', 'clients-secret.json')
GOOGLE_DRIVE_ACCESS_EMAILS = ['realclearneighborhoods1drive@gmail.com']

