from django.core.management import BaseCommand
from external_services.services.gspreadsheet import GoogleSpreadsheet
import datetime


class Command(BaseCommand):

    help = "Backup user data to google drive"

    def handle(self, *args, **options):
        self.stdout.write(
            datetime.datetime.now().strftime('Backup user data to google drive.'
                                             'Start at %Y-%m-%d %H:%M:%S')
        )
        gs = GoogleSpreadsheet()
        gs.send_to_cloud()
        self.stdout.write(
            datetime.datetime.now().strftime('Backup user data to google drive.'
                                             'Finish at %Y-%m-%d %H:%M:%S')
        )
