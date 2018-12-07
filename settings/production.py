from .base import *

logging.log(logging.INFO, 'loading settings for ' + __name__)

DEBUG = False
TEMPLATE_DEBUG = False

MANAGERS = ('ryan@realclearneighborhoods.com',)

EMAILTO = 'info@realclearneighborhoods.com'
EMAIL_HOST = 'mail.realclearneighborhoods.com'
EMAIL_HOST_USER = 'noreply@realclearneighborhoods.com'
EMAIL_HOST_PASSWORD = 'S$atur88e'
EMAIL_PORT = '26'
DEFAULT_FROM_EMAIL = "Real Clear Neighborhoods <noreply@realclearneighborhoods.com>"
SERVER_EMAIL = "ryan@realclearneighborhoods.com"
ONLINE_CONTACT_EMAIL = 'ryan@realclearneighborhoods.com'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'community_2015',
        'USER': 'admin', #'real_clear',
        'PASSWORD': '', #'realclearneighborhoods2015_databasepassword',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/tmp/webapp_cache',
        'TIMEOUT': 60,  # 60 seconds
    },
}

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
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': os.path.join(PROJECT_ROOT, 'logs', 'errors.log'),
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
        'webapp': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
        '': {
            'handlers': ['file'],
            'level': 'WARNING',
        },
    }
}

# https://api.salesforceiq.com
# https://help.salesforceiq.com/articles/set-up-api-access
SALESFORCEIQ = {
    'api_key': '59281da1e4b09b76f3c19ff6',
    'api_secret': 'aOu58cpBZxOhuzyGMiPlFj8AXox',
}

MAIL_CHIMP_USERNAME = 'Ryan Hodson'
MAIL_CHIMP_SECRET_KEY = 'f1740ea3fdfc7a43a5934872fe6cb3bf-us4'
MAIL_CHIMP_FROM_EMAIL = "info@realclearneighborhoods.com"
MAIL_CHIMP_LIST_ID = 'd31cc4d8e1'


# CELERY, REDIS

# https://stackoverflow.com/questions/18622630/setting-up-redis-on-webfaction
# to start redis-server on webfaction:
# cd ~/webapps/redis_app
# ./redis-server redis.conf

# to start celery worker on webfaction:
# celery multi start worker1 -A webapp --pidfile=$HOME/webapps/community_2015/apache2/logs/celery.pid --concurrency=1
# to stop celery workers:
# ps aux | grep 'celery worker' | awk '{print $2}' | xargs kill
BROKER_URL = 'redis://localhost:19785/0'
