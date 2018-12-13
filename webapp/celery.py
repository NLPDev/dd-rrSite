from __future__ import absolute_import
import os
import sys
from celery import Celery

if os.environ.get('DEVELOPMENT'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.development')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.production')

from django.conf import settings

sys.path.append(os.path.join(settings.BASE_DIR, 'third_party'))

app = Celery('celery_community')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

