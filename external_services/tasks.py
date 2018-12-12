from __future__ import absolute_import, unicode_literals
from celery import shared_task

from .services.salesforceiq import Client
from .services.mailchimp import RCNMailChimp

@shared_task
def salesforceiq_save_contact(neighbor):
    client = Client()
    client.save_contact(neighbor)

@shared_task
def mailchimp(neighbor):
    RCNMailChimp(instance=neighbor)
