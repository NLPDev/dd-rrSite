from django.core.management import BaseCommand

from external_services.services.salesforceiq import Client
from neighbor.models import Neighbor


class Command(BaseCommand):

    help = "uploads neighbors to SalesforceIQ service"

    def handle(self, *args, **options):
        self.stdout.write('statr upload neighbors')
        client = Client()
        for neighbor in Neighbor.objects.all():
            client.save_contact(neighbor)
        self.stdout.write('all neighbors have been uploaded')
