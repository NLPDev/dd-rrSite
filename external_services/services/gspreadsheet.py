from datetime import datetime

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from django.forms.models import model_to_dict

from neighbor.models import Neighbor
from django.conf import settings


class GoogleSpreadsheet(object):
    def __init__(self, credential=settings.GOOGLE_DRIVE_CREDENTIAL_FILE, **kwargs):
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive',
                 ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(credential, scope)
        self.client = gspread.authorize(creds)
        self.sheet_title = "Backup-{0}".format(datetime.now())
        self.sheet = self.client.create(self.sheet_title)
        for email in settings.GOOGLE_DRIVE_ACCESS_EMAILS:
            self.sheet.share(email, perm_type='user', role='writer')

    def send_to_cloud(self):
        csv = "First name,Last name,Address,City,State,ZIP-code,Email,Phone,Email\n"

        for neighbor in Neighbor.objects.all():
            # row = [x[1] for x in model_to_dict(neighbor).items()]

            address = "{0} {1}".format(neighbor.address_1,
                                       neighbor.address_2)

            row = [neighbor.first_name,
                   neighbor.last_name,
                   address,
                   neighbor.city,
                   neighbor.state,
                   neighbor.zip_code,
                   neighbor.email,
                   neighbor.phone,
                   neighbor.secondary_email,
                   "\n"]
            csv += ",".join(["" if x is None else x for x in row])
        self.client.import_csv(self.sheet.id, csv)
