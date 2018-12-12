import json, requests
from django.core.mail import send_mail
from django.conf import settings


class NeighborContact(object):
    """class that helps format Neighbor instance into a dict
        compatible with salesforceiq contact object"""
    fields_map = [
        {'field_id': '4', 'resolver': 'first_name_resolver'},
        {'field_id': '5', 'resolver': 'last_name_resolver'},
        {'field_id': '6', 'resolver': 'community_resolver'},
        {'field_id': '7', 'field_name': 'secondary_phone'},
        {'field_id': '8', 'field_name': 'secondary_email'},
        {'field_id': '9', 'field_name': 'lot_number'},
        {'field_id': '10', 'field_name': 'address_1'},
        {'field_id': '11', 'field_name': 'address_2'},
        {'field_id': '12', 'field_name': 'address_1', 'resolver': 'general_mailing_resolver'},
        {'field_id': '13', 'field_name': 'address_2', 'resolver': 'general_mailing_resolver'},
        {'field_id': '14', 'field_name': 'city', 'resolver': 'general_mailing_resolver'},
        {'field_id': '15', 'field_name': 'state', 'resolver': 'general_mailing_resolver'},
        {'field_id': '16', 'field_name': 'zip_code', 'resolver': 'general_mailing_resolver'},
        {'field_id': '18', 'field_name': 'city'},
        {'field_id': '19', 'field_name': 'zip_code'},
        {'field_id': '20', 'field_name': 'state'},
        {'field_id': '21', 'field_name': 'phone'},
        {'field_id': '22', 'resolver': 'db_email_resolver'},
        {'field_id': '17', 'resolver': 'extra_properties_resolver'},
        {'field_id': 'address', 'resolver': 'address_resolver'},
        {'field_id': 'email', 'resolver': 'email_resolver'},
        {'field_id': 'name', 'resolver': 'name_resolver'},
        {'field_id': 'phone', 'resolver': 'phone_resolver'},
    ]

    def __init__(self, neighbor):
        self.neighbor = neighbor

    def prepare_data(self):
        result_data = {}
        for x in self.fields_map:
            resolver = x.get('resolver')
            if resolver:
                value = getattr(self, resolver)(x.get('field_name'))
            else:
                value = self.general_resolver(x['field_name'])
            if value:
                result_data[x['field_id']] = value
        return {'properties': result_data}

    def general_resolver(self, field_name):
        value = getattr(self.neighbor, field_name)
        if value:
            return [{'value': str(value)}]

    def phone_resolver(self, *args):
        result = []
        if self.neighbor.phone:
            result.append({
                'value': self.neighbor.phone,
                'metadata': {'primary': 'true', 'stype': 'phone'}
            })
        if self.neighbor.secondary_phone:
            result.append({
                'value': self.neighbor.secondary_phone,
                'metadata': {'primary': 'false', 'stype': 'secondary'}
            })
        return result

    def name_resolver(self, *args):
        return [{'value': '%s %s' % (self.neighbor.user.first_name, self.neighbor.user.last_name)}]

    def first_name_resolver(self, *args):
        return [{'value': self.neighbor.user.first_name}]

    def last_name_resolver(self, *args):
        return [{'value': self.neighbor.user.last_name}]

    def address_resolver(self, *args):
        result = []
        address = self.neighbor.address_1
        if address:
            if self.neighbor.address_2:
                address = '%s, %s' % (address, self.neighbor.address_2)
            result.append({
                'value': address,
                'metadata': {'primary': 'true', 'stype': 'main'}
            })
        if hasattr(self.neighbor, 'mailingaddress'):
            address = self.neighbor.mailingaddress.address_1
            if self.neighbor.mailingaddress.address_2:
                address = '%s, %s' % (address, self.neighbor.mailingaddress.address_2)
            result.append({
                'value': address,
                'metadata': {'primary': 'false', 'stype': 'mailing'}
            })
        return result

    def general_mailing_resolver(self, field_name):
        if hasattr(self.neighbor, 'mailingaddress'):
            value = getattr(self.neighbor.mailingaddress, field_name)
            if value:
                return [{'value': value}]

    def email_resolver(self, *args):
        result = []
        result.append({
            'value': self.neighbor.user.email,
            'metadata': {'primary': 'true', 'stype': 'email'}
        })
        if self.neighbor.secondary_email:
            result.append({
                'value': self.neighbor.secondary_email,
                'metadata': {'primary': 'false', 'stype': 'secondary'}
            })
        return result

    def community_resolver(self, *args):
        if self.neighbor.community:
            return [{'value': self.neighbor.community.name}]

    def extra_properties_resolver(self, *args):
        numbers = [x.lot_number for x in self.neighbor.extraproperty_set.all()]
        if numbers:
            return [{'value': x} for x in numbers]

    def db_email_resolver(self, *args):
        return [{'value': self.neighbor.user.email}]


class Client(object):
    """salesforceiq client"""
    api_url = 'https://api.salesforceiq.com/v2'
    contact_url = 'https://api.salesforceiq.com/v2/contacts'

    def __init__(self):
        conf = settings.SALESFORCEIQ
        get_headers = {'Accept': 'application/json'}
        post_headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        auth = (conf['api_key'], conf['api_secret'])
        self.post_kwargs = {'auth': auth, 'headers': post_headers}
        self.get_kwargs = {'auth': auth, 'headers': get_headers}

    def send_error_mail(self, content):
        send_mail('saleforceiq error', content,
              settings.DEFAULT_FROM_EMAIL, [settings.EMAILTO])

    def get_contact(self, contact_id):
        url = '%s/%s' % (self.contact_url, contact_id)
        r = requests.get(url, **self.get_kwargs)
        return r

    def create_contact(self, neighbor):
        """creates salesforciq contact and saves salesforceiq id into Neighbor"""
        contact = NeighborContact(neighbor)
        data = json.dumps(contact.prepare_data())
        r = requests.post(self.contact_url, data=data, **self.post_kwargs)
        if r.status_code == 200:
            response_data = r.json()
            neighbor.salesforceiq_id = response_data['id']
            neighbor.save(update_fields=['salesforceiq_id'])
        else:
            self.send_error_mail(
                'Error on create contact. Neighbor id: %s. salesforceiq response: %s'
                % (neighbor.id, r.content)
            )
        return r

    def update_contact(self, neighbor):
        """updates salesforceiq contact"""
        contact = NeighborContact(neighbor)
        data = contact.prepare_data()
        data['id'] = neighbor.salesforceiq_id
        data = json.dumps(data)
        url = '%s/%s' % (self.contact_url, neighbor.salesforceiq_id)
        r = requests.put(url, data=data, **self.post_kwargs)
        if r.status_code != 200:
            self.send_error_mail(
                'Error on update contact. Neighbor id: %s. salesforceiq response: %s'
                % (neighbor.id, r.content)
            )
        return r

    def delete_contact(self, neighbor):
        """archive salesforciq contact"""
        url = '%s/%s' % (self.contact_url, neighbor.salesforceiq_id)
        r = requests.delete(url, **self.get_kwargs)
        return r

    def save_contact(self, neighbor):
        if neighbor.salesforceiq_id:
            return self.update_contact(neighbor)
        else: 
            return self.create_contact(neighbor)
