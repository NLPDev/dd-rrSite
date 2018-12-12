from __init__ import BaseServiceFunctionality
from mailchimp3 import MailChimp
from django.conf import settings


class RCNMailChimp(BaseServiceFunctionality):

    def __init__(self, **kwargs):
        super(RCNMailChimp, self).__init__(**kwargs)

        self.client = MailChimp(settings.MAIL_CHIMP_USERNAME, settings.MAIL_CHIMP_SECRET_KEY)
        self.main()

    def main(self):
        if self.instance.mailchimp_subscriber_id:
            self.update_member(settings.MAIL_CHIMP_LIST_ID,
                               self.instance.mailchimp_subscriber_id)
        else:
            self.create_member(settings.MAIL_CHIMP_LIST_ID)

    def create_member(self, list_id):
        data = {
            'email_address': self.instance.email,
            'status': 'subscribed',
            'merge_fields': {
                'FNAME': self.instance.first_name,
                'LNAME': self.instance.last_name,
            },
        }
        response = self.client.lists.members.create(list_id=list_id, data=data)
        if response.get('id'):
            self.instance.mailchimp_subscriber_id = response['id']
            self.instance.save(update_fields=['mailchimp_subscriber_id'])
        return self.instance.mailchimp_subscriber_id

    def update_member(self, list_id, subscriber_hash):
        data = {
            'email_address': self.instance.email,
            'status': 'subscribed',
            'merge_fields': {
                'FNAME': self.instance.first_name,
                'LNAME': self.instance.last_name,
            },
        }
        response = self.client.lists.members.update(
        # response = self.client.lists.members.create_or_update(
            list_id=list_id,
            subscriber_hash=subscriber_hash,
            data=data
        )
        if response.get('id'):
            self.instance.mailchimp_subscriber_id = response['id']
            self.instance.save(update_fields=['mailchimp_subscriber_id'])
        return self.instance.mailchimp_subscriber_id

    def get_list(self):
        try:
            response = self.client.lists.get(list_id=self.instance.community.mailchimp_neighborhood_id)
        except Exception :
            response = {}
        return response['id'] if response.get('id') else False

    def create_list(self):
        # Need to add company contact data!
        data = {
            "name": self.instance.community.name,
            "contact": {
                "company": "RealClearNeighborhoods",
                "address1": "",
                "address2": "",
                "city": self.instance.community.city,
                "state": self.instance.community.state,
                "zip": self.instance.community.zip_code,
                "country": "US",
                "phone": "",
            },
            "permission_reminder": "You're receiving this email because you signed up for updates about "
                                   "RealClearNeighborhoods's newest hats.",
            "campaign_defaults": {
                "from_name": self.instance.community.name,
                "from_email": settings.MAIL_CHIMP_FROM_EMAIL,
                "subject": "",
                "language": "en",
            },
            "email_type_option": True
        }
        response = self.client.lists.create(data=data)
        if response.get('id'):
            community = self.instance.community
            community.mailchimp_neighborhood_id = response['id']
            community.save()

        return response.get('id')
