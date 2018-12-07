from .base import *

logging.log(logging.INFO, 'loading settings for ' + __name__)

DEBUG = True
TEMPLATE_DEBUG = True
DEVELOPMENT = True


# EMAIL SETTINGS
EMAILTO = 'dev@millcreeksoftware.biz'
EMAIL_HOST = 'smtp.webfaction.com'
EMAIL_HOST_USER = 'millcreek_noreply'
EMAIL_HOST_PASSWORD = 'jupit99'
EMAIL_PORT = '25'
DEFAULT_FROM_EMAIL = "Millcreek Software <noreply@millcreeksoftware.biz>"
SERVER_EMAIL = "kellym@millcreeksoftware.biz"
ONLINE_CONTACT_EMAIL = 'dev@millcreeksoftware.biz'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'sqlite/local.db'),
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    },
}

SESSION_COOKIE_AGE = 7200
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

STRIPE_SECRET_KEY = 'sk_test_2Lv1O2wucGSB89TiyRzks822'
STRIPE_PUBLIC_KEY = 'pk_test_jtr2ZzzfTykZqohGGOSvYpAA'

try:
    from .local_settings import *
except ImportError:
    pass