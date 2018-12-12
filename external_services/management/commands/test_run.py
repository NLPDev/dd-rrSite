from django.core.management import BaseCommand
from external_services.services.mailchimp import RCNMailChimp

from neighbor.models import Neighbor

class Command(BaseCommand):

    help = "My test command"

    def handle(self, *args, **options):
        RCNMailChimp(instance=Neighbor.objects.last())
        self.stdout.write("Doing All The Things!")

