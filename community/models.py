from django.db import models
from django.contrib.sites.models import Site
from django.template.defaultfilters import slugify


class Community(models.Model):
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

    STATE_CHOICES_ABBREVIATED = [
        ('AL', 'AL'), ('AK', 'AK'), ('AZ', 'AZ'), ('AR', 'AR'),
        ('CA', 'CA'), ('CO', 'CO'), ('CT', 'CT'), ('DE', 'DE'), ('DC', 'DC'),
        ('FL', 'FL'), ('GA', 'GA'), ('HI', 'HI'), ('ID', 'ID'), ('IL', 'IL'), ('IN', 'IN'),
        ('IA', 'IA'), ('KS', 'KS'), ('KY', 'KY'), ('LA', 'LA'), ('ME', 'ME'), ('MD', 'MD'),
        ('MA', 'MA'), ('MI', 'MI'), ('MN', 'MN'), ('MS', 'MS'), ('MO', 'MO'),
        ('MT', 'MT'), ('NE', 'NE'), ('NV', 'NV'), ('NH', 'NH'), ('NJ', 'NJ'),
        ('NM', 'NM'), ('NY', 'NY'), ('NC', 'NC'), ('ND', 'ND'), ('OH', 'OH'),
        ('OK', 'OK'), ('OR', 'OR'), ('PA', 'PA'), ('PR', 'PR'), ('RI', 'RI'),
        ('SC', 'SC'), ('SD', 'SD'), ('TN', 'TN'), ('TX', 'TX'), ('UT', 'UT'), ('VT', 'VT'),
        ('VA', 'VA'), ('WA', 'WA'), ('WV', 'WV'), ('WI', 'WI'), ('WY', 'WY'),
    ]

    name = models.CharField(max_length=100, verbose_name='Name')
    mailchimp_neighborhood_id = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=2, choices=STATE_CHOICES, blank=True, null=True)
    zip_code = models.CharField(max_length=10, blank=True, null=True)

    slug = models.SlugField(verbose_name='Web Path')
    site = models.ForeignKey(Site, blank=True, null=True)  # for associated sub domains
    created_on = models.DateTimeField(auto_now_add=True)

    # Stripe API will be per Community. I'm including both test and prod key fields
    # just in case we have a need to debug one Community.
    production_public = models.CharField(max_length=200, blank=True, null=True)
    production_secret = models.CharField(max_length=200, blank=True, null=True)
    testing_public = models.CharField(max_length=200, blank=True, null=True)
    testing_secret = models.CharField(max_length=200, blank=True, null=True)

    # To enable DEBUG mode on a neighborhood, make this true.
    debug_mode = models.BooleanField(default=False)

    """
       Never reference the key fields directly, only ever use the following properties.
       This is so we don't have to have checks anytime we make a stripe call to see if
       we are in test mode or live mode, and then grab the appropriate keys. This will
       do it for you. As of now, it's only one property, community.keys, which returns
       a dictionary in the form of {'public': xxxxx, 'secret': xxxxx}.
       TODO: Discuss if we want two properties and why; I like just one clean one.
    """
    @property
    def keys(self):
        # If we're in test mode, return the test keys. Otherwise, give us the real stuff.
        if self.debug_mode:
            keys = {'public': self.testing_public, 'secret': self.testing_secret}
            return keys

        keys = {'public': self.production_public, 'secret': self.production_secret}
        return keys

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)

        super(Community, self).save(*args, **kwargs)

        # Auto create calendar when communities are created.
        if not self.pk or kwargs.get('force_insert', True):
            new_calendar = Calendar.objects.create(community=self)
            new_calendar.save()

        super(Community, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = "Community"
        verbose_name_plural = "Communities"

    @property
    def calendar(self):
        return self.calendar_set.all()[0]

    @property
    def services(self):
        return self.reservableservices_set.filter(is_approved=True)

    @property
    def announcements(self):
        return self.announcement_set.filter(is_approved=True, is_cancelled=False)

    @property
    def service_providers(self):
        return self.serviceprovider_set.filter(is_approved=True)

    def get_pending_announcements(self):
        return self.announcement_set.filter(is_approved=False, is_cancelled=False)

    def get_pending_service_providers(self):
        return self.serviceprovider_set.filter(is_approved=False)


class Calendar(models.Model):
    community = models.ForeignKey(Community)

    @property
    def events(self):
        return self.calendarevent_set.all().filter(is_approved=True, is_cancelled=False)

    def get_month(self, year, month):
        return self.calendarevent_set.filter(start_date__month=month, start_date__year=year, is_approved=True, is_cancelled=False)

    def get_day(self, year, month, day):
        return self.calendarevent_set.filter(start_date__month=month, start_date__year=year, start_date__day=day, is_approved=True, is_cancelled=False).order_by('start_date')

    def __unicode__(self):
        return self.community.name + ' Calendar'


def document_filename(instance, filename):
    return '/'.join(['documents', instance.community.slug, filename])

class Document(models.Model):

    community = models.ForeignKey(Community)
    document = models.FileField(upload_to=document_filename)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = "Community Document"
        verbose_name_plural = "Community Documents"
