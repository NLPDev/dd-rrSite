import datetime
from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError

from django.db import models
from django.contrib.auth.models import User

from easy_thumbnails.fields import ThumbnailerImageField

from community.models import Community, Calendar
from dues.models import Dues


class Neighbor(models.Model):

    CONTACT_METHOD_CHOICES = (('email', 'Email'), ('phone', 'Phone'))
    ACCOUNT_TYPE_CHOICES = ((1, 'Homeowner'), (2, 'Multiple Lot Owner'), (3, 'Property Manager'))

    user = models.OneToOneField(User)
    account_type = models.PositiveIntegerField(choices=ACCOUNT_TYPE_CHOICES, null=True, blank=False)
    company_name = models.CharField(max_length=150, null=True, blank=True)
    # allowed to be blank,
    # but community selection form will always be shown to this user when they login.
    # see neighbor/middleware/neighbor.py
    # deprecated
    community = models.ForeignKey(Community, related_name='Community', blank=True, null=True)
    communities = models.ManyToManyField(Community, related_name='neighbors',
                                         blank=True, null=True, through='NeighborCommunity')
    phone = models.CharField(max_length=20, blank=True, null=True)
    # deprecated
    secondary_phone = models.CharField(max_length=20, blank=True, null=True)
    # deprecated
    secondary_email = models.EmailField(blank=True, null=True)
    # deprecated
    lot_number = models.PositiveIntegerField(blank=True, null=True)
    # deprecated
    address_1 = models.CharField(max_length=100, blank=True, null=True)
    # deprecated
    address_2 = models.CharField(max_length=100, blank=True, null=True)
    billing_address_1 = models.CharField(max_length=100, null=True, blank=False)
    billing_address_2 = models.CharField(max_length=100, null=True, blank=False)
    billing_city = models.CharField(max_length=50, blank=False, null=True)
    billing_state = models.CharField(max_length=2, choices=Community.STATE_CHOICES, blank=False, null=True)
    billing_zip_code = models.CharField(max_length=10, blank=False, null=True)
    
    city = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=2, choices=Community.STATE_CHOICES, blank=True, null=True)
    zip_code = models.CharField(max_length=10, blank=True, null=True)
    # deprecated
    preferred_contact_method = models.CharField(max_length=20, choices=CONTACT_METHOD_CHOICES, blank=True, null=True)
    # deprecated
    position = models.CharField(max_length=100, blank=True, null=True)
    salesforceiq_id = models.CharField(max_length=50, blank=True, null=True)
    mailchimp_subscriber_id = models.CharField(max_length=100, blank=True, null=True)

    def __unicode__(self):
        return '{}, {}'.format(self.user.last_name, self.user.first_name)

    def save(self, *args, **kwargs):
        super(Neighbor, self).save(*args, **kwargs)

        # Create a wallet for every new neighbor, but only on creation, not every subsequent save.
        if not self.pk or kwargs.get('force_insert', True):
            new_wallet = Wallet.objects.create(neighbor=self)
            new_wallet.save()

            # Check if there are any active dues on the community, and if so, set them up.
            if self.community:
                if len(self.community.dues_set.all()) > 0:
                    for dues in self.community.dues_set.all():
                        if dues.is_active:
                            new_dues = DuePayment.objects.create(neighbor=self, dues=dues)
                            new_dues.save()

    def get_outstanding_violations(self):
        return self.violationevent_set.filter(is_paid=False, is_approved=True)

    def get_past_due_violations(self):
        return self.violationevent_set.filter(past_due=True)

    def get_past_due_dues(self):
        return self.dues_set.filter(past_due=True)

    @property
    def first_name(self):
        return self.user.first_name

    @property
    def last_name(self):
        return self.user.last_name

    @property
    def email(self):
        return self.user.email

    @property
    def wallet(self):
        return self.wallet_set.all()[0]

    @property
    def can_add_property(self):
        return self.account_type != 1 or not self.realproperty_set.exists()


class NeighborCommunity(models.Model):
    neighbor = models.ForeignKey(Neighbor, on_delete=models.CASCADE)
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    position = models.CharField(max_length=100)

    class Meta():
        unique_together = ('neighbor', 'community')


class MailingAddress(models.Model):
    neighbor = models.OneToOneField(Neighbor, blank=True, null=True, on_delete=models.CASCADE)
    address_1 = models.CharField(max_length=100, blank=True, null=True)
    address_2 = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=2, choices=Community.STATE_CHOICES, blank=True, null=True)
    zip_code = models.CharField(max_length=10, blank=True, null=True)


class RealProperty(models.Model):
    neighbor = models.ForeignKey(Neighbor, blank=True, null=True, on_delete=models.SET_NULL)
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    lot_number = models.CharField(max_length=5)
    # one address just two lines for address
    address_1 = models.CharField(max_length=100)
    address_2 = models.CharField(max_length=100, blank=True, default='')
    city = models.CharField(max_length=50, blank=True, default='')
    state = models.CharField(max_length=2, choices=Community.STATE_CHOICES)
    zip_code = models.CharField(max_length=10)
    contact = models.CharField(max_length=100, blank=True, default='')

    class Meta():
        unique_together = ('community', 'lot_number')


class AddressConflict(models.Model):
    existing_neighbor = models.ForeignKey(Neighbor)
    new_neighbor_first = models.CharField(max_length=50)
    new_neighbor_last = models.CharField(max_length=50)
    new_neighbor_phone = models.CharField(max_length=50)
    new_neighbor_email = models.EmailField(max_length=256)

    is_resolved = models.BooleanField(default=False)


class Wallet(models.Model):
    neighbor = models.ForeignKey(Neighbor)

    @property
    def transaction_history(self):
        return self.transactions_set.all().order_by('-date')

    @property
    def saved_cards(self):
        return self.cards_set.all().order_by('exp_date')

    @property
    def get_payments(self):
        payments = []

        # Violation Events
        for violation in self.neighbor.violationevent_set.filter(is_approved=True, is_paid=False):
            payments.append(violation)

        # Dues
        for dues in self.neighbor.duepayment_set.filter(is_active=True, is_paid=False):
            payments.append(dues)

        return payments

    def create_card(self, title, type, last_four, exp_date, token, b_name, b_addr1=None, b_addr2=None, b_city=None, b_state=None, b_zip=None):
        Cards.objects.create(wallet=self, title=title, type=type, last_four=last_four, exp_date=exp_date,
                             token=token, billing_name=b_name, billing_address_1=b_addr1, billing_address_2=b_addr2,
                             billing_city=b_city, billing_state=b_state, billing_zipcode=b_zip)

    def delete_card(self, card_id, card_title):

        if card_id and card_title:
            Cards.objects.get(id=card_id, title=card_title).delete()

        elif card_id and not card_title:
            Cards.objects.get(id=card_id).delete()

        elif card_title and not card_id:
            Cards.objects.get(title=card_title).delete()

        else:
            return 'Couldn\'t find the card to delete'


class Transactions(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('V', 'DUES/VIOLATIONS'),
        ('R', 'RESERVATION')
    ]

    wallet = models.ForeignKey(Wallet)
    title = models.CharField(max_length=50)
    transaction_type = models.CharField(max_length=2, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(decimal_places=2, max_digits=9)
    date = models.DateTimeField(auto_now_add=True)

    # Stripe metadata
    stripe_id = models.CharField(max_length='200', blank=True, null=True)
    failure_code = models.CharField(max_length=50, blank=True, null=True)
    failure_message = models.TextField(blank=True, null=True)
    stripe_paid = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Transactions'
        verbose_name = 'Transaction'

    def __unicode__(self):
        return u'{}'.format(self.title)

    def stripe(self, **kwargs):
        import stripe

        key = kwargs.pop('keys').get('secret')
        stripe.api_key = key

        # Set up variables
        amount = kwargs.pop('amount')
        card = kwargs.pop('card')
        description = kwargs.pop('description')
        metadata = kwargs.pop('metadata')

        try:
            stripe_response = stripe.Charge.create(amount=amount, currency="usd", card=card,
                                                   description=description, metadata=metadata)

            if 'id' in stripe_response:
                self.stripe_id = stripe_response['id']

            if 'failure_code' in stripe_response:
                self.failure_code = stripe_response['failure_code']

            if 'failure_message' in stripe_response:
                self.failure_message = stripe_response['failure_message']

            if 'paid' in stripe_response:
                self.stripe_paid = stripe_response['paid']

            return True

        except stripe.CardError, e:
            # Card error, customer end. Send back to form and have neighbor redo.
            self.failure_code = 'CardError'
            self.failure_message = e
            return e

        except stripe.InvalidRequestError, e:
            # Parameters on server side are wrong. Log it, fail out, and retry transaction.
            self.failure_code = 'InvalidRequestError'
            self.failure_message = e
            return e

        except stripe.AuthenticationError, e:
            # Secret API key is wrong. Log it, fail, and retry.
            self.failure_code = 'AuthenticationError'
            self.failure_message = e
            return e

        except stripe.APIConnectionError, e:
            self.failure_code = 'APIConnectionError'
            self.failure_message = e
            return e

        except stripe.StripeError, e:
            # Failure on the Stripe network end. Log it, Fail.
            self.failure_code = 'StripeError'
            self.failure_message = e
            return e

        except Exception, e:
            # Something completely unexpected. Fail Loudly, probably.
            self.failure_code = 'UNKNOWN'
            self.failure_message = e
            return e


class Cards(models.Model):
    CARD_TYPE_CHOICES = [('V', 'VISA'), ('MC', 'MASTERCARD'), ('AMEX', 'AMERICAN EXPRESS'), ('D', 'DISCOVER')]
    STATE_CHOICES = [
        ('AL', 'Alabama'), ('AK', 'Alaska'), ('AZ', 'Arizona'), ('AR', 'Arkansas'),
        ('CA', 'California'), ('CO', 'Colorado'), ('CT', 'Connecticut'), ('DE', 'Delaware'), ('DC', 'District of Columbia'),
        ('FL', 'Florida'), ('GA', 'Georgia'), ('HI', 'Hawaii'), ('ID', 'Idaho'), ('IL', 'Illinois'), ('IN', 'Indiana'),
        ('IA', 'Iowa'), ('KS', 'Kansas'), ('KY', 'Kentucky'), ('LA', 'Louisiana'), ('ME', 'Maine'), ('MD', 'Maryland'),
        ('MA', 'Massachusetts'), ('MI', 'Michigan'), ('MN', 'Minnesota'), ('MS', 'Mississippi'), ('MO', 'Missouri'),
        ('MT', 'Montana'), ('NE', 'Nebraska'), ('NV', 'Nevada'), ('NH', 'New Hampshire'), ('NJ', 'New Jersey'),
        ('NM', 'New Mexico'), ('NY', 'New York'), ('NC', 'North Carolina'), ('ND', 'North Dakota'), ('OH', 'Ohio'),
        ('OK', 'Oklahoma'), ('OR', 'Oregon'), ('PA', 'Pennsylvania'), ('PR', 'Puerto Rico'), ('RI', 'Rhode Island'),
        ('SC', 'South Carolina'), ('SD', 'South Dakota'), ('TN', 'Tennessee'), ('TX', 'Texas'), ('UT', 'Utah'), ('VT', 'Vermont'),
        ('VA', 'Virginia'), ('WA', 'Washington'), ('WV', 'West Virginia'), ('WI', 'Wisconsin'), ('WY', 'Wyoming'),
    ]

    wallet = models.ForeignKey(Wallet)
    title = models.CharField(max_length=30)
    type = models.CharField(max_length=15, choices=CARD_TYPE_CHOICES)
    last_four = models.IntegerField(max_length=4)
    exp_date = models.DateField()
    token = models.CharField(max_length=60)
    security_code = models.CharField(max_length=4)

    # Billing Information
    billing_name = models.CharField(max_length=50)
    billing_address_1 = models.CharField(max_length=50)
    billing_address_2 = models.CharField(max_length=50, blank=True, null=True)
    billing_city = models.CharField(max_length=50)
    billing_state = models.CharField(max_length=2, choices=STATE_CHOICES)
    billing_zipcode = models.CharField(max_length=20)

    def get_billing_info(self):
        billing_info = {
            'name': self.billing_name,
            'address_line1': self.billing_address_1,
            'address_line2': self.billing_address_2,
            'address_city': self.billing_city,
            'address_state': self.billing_state,
            'address_zip': self.billing_zipcode,
            'exp_month': self.exp_date.month,
            'exp_year': self.exp_date.year,
            'cvc': self.security_code
        }

        return billing_info

    @property
    def is_expired(self):
        if datetime.datetime.today() > self.exp_date:
            return True
        else:
            return False

    def __unicode__(self):
        return '{} - {}'.format(self.title, self.last_four)


class DuePayment(models.Model):
    neighbor = models.ForeignKey(Neighbor)
    dues = models.ForeignKey(Dues)
    is_paid = models.BooleanField(default=False, verbose_name='Paid')
    is_due = models.BooleanField(default=True, verbose_name='Due')
    is_active = models.BooleanField(default=True, verbose_name='Active')

    # TODO: Implement pay_frequency and due_date logic. Add due_date field.

    # Payment Association
    transaction = models.ForeignKey(Transactions, blank=True, null=True)

    @property
    def amount(self):
        return Decimal(self.dues.fee)

    @property
    def title(self):
        return self.dues.title

    def mark_paid(self, transaction):
        self.transaction = transaction
        self.is_paid = True
        self.save()

    def __unicode__(self):
        return self.dues.title


# Calendar Events, Neighbor Based
class CalendarEvent(models.Model):

    calendar = models.ForeignKey(Calendar)
    neighbor = models.ForeignKey(Neighbor)

    title = models.CharField(max_length=50, verbose_name='Event Title')
    location = models.CharField(max_length=100, verbose_name='Event Location')
    start_date = models.DateTimeField(verbose_name='Start Time')
    end_date = models.DateTimeField(verbose_name='End Time')
    description = models.TextField(blank=True, null=True, verbose_name='Event Description')

    # Contact info. Init the form with info from neighbor.
    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=40)
    phone = models.CharField(max_length=12)
    email = models.EmailField(blank=True, null=True)

    is_approved = models.BooleanField(default=False)
    is_denied = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Calendar Events'
        verbose_name = 'Calendar Event'

    def save(self, *args, **kwargs):
        self.calendar = self.neighbor.community.calendar

        super(CalendarEvent, self).save(*args, **kwargs)

    def get_photoset(self):
        return self.eventphoto_set.all()


def validate_photo(fieldfile_obj):
        filesize = fieldfile_obj.file.size
        if filesize > settings.MAX_FILESIZE*1024*1024:
            raise ValidationError("Image exceeds max filesize of %s MB" % str(settings.MAX_FILESIZE))

class EventPhoto(models.Model):

    event = models.ForeignKey(CalendarEvent)
    photo = ThumbnailerImageField(upload_to='calendar/%Y/%m/%d', blank=True, null=True, validators=[validate_photo])

    def __unicode__(self):
        return self.event.title
