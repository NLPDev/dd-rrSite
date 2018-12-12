from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from external_services.services.mailchimp import RCNMailChimp
from neighbor.models import Neighbor
from . import tasks


@receiver(post_save, sender=Neighbor, dispatch_uid="mailchimp_save")
def mail_chimp(sender, instance, created, **kwargs):
    update_fields = kwargs['update_fields'] or []
    if 'mailchimp_subscriber_id' not in update_fields and\
       'salesforceiq_id' not in update_fields:
        if hasattr(settings, 'MAIL_CHIMP_USERNAME') and \
           hasattr(settings, 'MAIL_CHIMP_SECRET_KEY'):
            tasks.mailchimp.apply_async(
                kwargs={'neighbor': instance}, countdown=1,
            )


@receiver(post_save, sender=Neighbor, dispatch_uid="salesforceiq_save")
def salesforceiq(sender, instance, created, **kwargs):
    update_fields = kwargs['update_fields'] or []
    if (
        hasattr(settings, 'SALESFORCEIQ') and settings.SALESFORCEIQ
        and 'salesforceiq_id' not in update_fields
        and 'mailchimp_subscriber_id' not in update_fields
    ):
        tasks.salesforceiq_save_contact.apply_async(
            kwargs={'neighbor': instance}, countdown=1,
        )
