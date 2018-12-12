from django.core.management import BaseCommand
from external_services.services.mailchimp import RCNMailChimp

from neighbor.models import Neighbor
from django.conf import settings


class Command(BaseCommand):

    help = "exports neighbors to mailchimp"

    def handle(self, *args, **options):
        email = ''
        for n in Neighbor.objects.all().order_by('user__email'):
            # check to exclude dublicate emails
            if n.email.lower() == email:
                continue
            self.stdout.write(
                "Add neighbor {} {}, id = {}, email = {} email to confirm = {}".format(n.first_name, n.last_name, n.id, n.email, email)
            )
            RCNMailChimp(instance=n)
            email = n.email.lower()
        self.stdout.write("All neighbors added in list:"+settings.MAIL_CHIMP_LIST_ID)

